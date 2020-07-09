# -*- coding: utf-8 -*-

"""
Created on Wed Jan 2020
@authors: David Ethier  david.ethier2@usherbrooke.ca
          Luca Romanini luca.romanini@usherbrooke.ca

"""

# Import des librairies
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import os
from osgeo import gdal
import osr
from gdalconst import *
import pandas as pd
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from sklearn import metrics
from sklearn.metrics import confusion_matrix
from sklearn.metrics import plot_confusion_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import validation_curve # A mettre dans fonctions modele
from sklearn.feature_selection import SelectFromModel
from sklearn.utils import resample
from ech_pixel import creation_cadre
from pretraitements import clip_raster_to_polygon

import seaborn as sns


def model_plots(test_y, clf, test_metriques, metriques):
    # Matrice de confusion
    #c_matrice = confusion_matrix(test_y, y_pred)

    # disp = plot_confusion_matrix(clf, test_metriques, test_y,
    #                              cmap=plt.cm.Blues,
    #                              values_format='d')
    # disp.ax_.set_title('Matrice de confusion à 12 métriques')
    # plt.xlabel('Prédit')
    # plt.ylabel('Réel')

    # Importances des metriques
    importances = clf.feature_importances_
    indices = np.argsort(importances)
    indices_list = [metriques[i] for i in indices]

    # plot them with a horizontal bar chart
    # plt.figure()  # Crée une nouvelle instance de graphique
    # plt.title('Importances des métriques')
    # plt.barh(range(len(indices)), importances[indices], color='b', align='center')
    # plt.yticks(range(len(indices)), [metriques[i] for i in indices])
    # plt.xlabel('Importance relative (%)')
    # plt.show(block=False)

    return indices_list

def entrainement_pix (inputEch, metriques, outputMod, replaceMod, makeplots, **kwargs):
    # Pour importer un shapefile
    # # On crée la liste des shapefiles
    files = os.listdir(inputEch)  # Liste des fichiers dans le dossier "folder"
    shp_list = [os.path.join(inputEch, i) for i in files if i.endswith('.shp')] # Obtenir une liste des chemins pour
                                                                                   # .shp seulement
    # On join les fichiers .shp de la liste
    new_shp = gpd.GeoDataFrame(pd.concat([gpd.read_file(i) for i in shp_list],
                                          ignore_index = True), crs = gpd.read_file(shp_list[0]).crs)

    # On choisi la colonne de que l'on veut prédire (ici le type de dépots)
    y_depots = new_shp.Zone

    # On definit les métriques sur lesquels on veut faire l'analyse
    X_metriques = new_shp[metriques]

    # Séparation des données en données d'entrainement et données de tests
    train_metriques, test_metriques, train_y, test_y = train_test_split(X_metriques, y_depots, test_size=0.30, random_state = 22)

    # Create a Gaussian Classifier
    #clf = RandomForestClassifier(n_estimators = 15000, verbose = 2, oob_score = True, random_state = 42)
    clf = RandomForestClassifier(verbose=2, oob_score=True, random_state=42, **kwargs)

    # Train the model using the training sets y_pred=clf.predict(X_test)
    clf.fit(train_metriques, train_y)     # Model fit sur 70%
    y_pred = clf.predict(test_metriques)  # Predicition sur 30%

    # Save the model as a pickle in a file
    if replaceMod is True:
        print(inputEch[-5:])
        #joblib.dump(clf, '{}.pkl'.format(outputMod))
        joblib.dump(clf, '{}.pkl'.format(outputMod))


    # Impression de précision
    accu_mod = metrics.accuracy_score(test_y, y_pred)
    print("Accuracy:", accu_mod)

    # Génération des graphiques (Appel de fonction)
    if makeplots is True:
       model_plots(test_y=test_y, clf=clf, test_metriques=test_metriques, metriques=metriques)

    #return clf, plt, accu_mod
    return clf, accu_mod, train_metriques, train_y, test_metriques, test_y

def entrainement_obj(inputEch, outputMod, replaceMod, makeplots, **kwargs):
    # Pour importer un shapefile
    # # On crée la liste des shapefiles
    files = os.listdir(inputEch)  # Liste des fichiers dans le dossier "folder"
    shp_list = [os.path.join(inputEch, i) for i in files if i.endswith('.shp')] # Obtenir une liste des chemins pour
                                                                                   # .shp seulement
    # On join les fichiers .shp de la liste
    new_shp_temp = gpd.GeoDataFrame(pd.concat([gpd.read_file(i) for i in shp_list],
                                              ignore_index=True), crs=gpd.read_file(shp_list[0]).crs)

    # On enleve la colonne 'label' et on enleve les rangées 'nulles'
    del_liste_base = ['CorH_media', 'CorH_media', 'CorH_mean', 'CorH_std', 'ANVAD_coun', 'ConH_count', 'CorH_count', 'CVA_count', 'DI_count',
                      'ED_count', 'MeaH_count', 'PC_count', 'Pen_count', 'SSDN_count', 'TPI_count', 'TWI_count']
    new_shp_temp = new_shp_temp.drop(del_liste_base, axis=1)
    print(new_shp_temp.columns)
    #new_shp_temp = new_shp_temp.drop(del_liste_feat, axis=1)
    # del new_shp_temp['CorH_media']
    # del new_shp_temp['CorH_mean']
    # del new_shp_temp['CorH_std']
    # del new_shp_temp['ANVAD_coun']
    # del new_shp_temp['ConH_count']
    # del new_shp_temp['CorH_count']
    # del new_shp_temp['CVA_count']
    # del new_shp_temp['DI_count']
    # del new_shp_temp['ED_count']
    # del new_shp_temp['MeaH_count']
    # del new_shp_temp['PC_count']
    # del new_shp_temp['Pen_count']
    # del new_shp_temp['SSDN_count']
    # del new_shp_temp['TPI_count']
    # del new_shp_temp['TWI_count']
    new_shp_temp = new_shp_temp.dropna()
    new_shp_temp = new_shp_temp.dropna()

    df_majority = new_shp_temp[new_shp_temp.Zone == 0]
    df_minority = new_shp_temp[new_shp_temp.Zone == 1]

    # Downsample majority class
    df_majority_downsampled = resample(df_majority,
                                       replace=False,  # sample without replacement
                                       n_samples=len(df_minority),  # to match minority class
                                       random_state=123)  # reproducible results

    # Combine minority class with downsampled majority class
    new_shp = pd.concat([df_majority_downsampled, df_minority])
    # print(new_shp.columns)
    # print(len(new_shp.columns))

    # On choisi la colonne de que l'on veut prédire (ici le type de dépots)
    y_depots = new_shp.Zone

    # On definit les métriques sur lesquels on veut faire l'analyse
    metriques = list(new_shp.iloc[:, 1:-2])
    # print(metriques)
    # print(len(metriques))
    X_metriques = new_shp[metriques]
    print(metriques)

    # Séparation des données en données d'entrainement et données de tests
    train_metriques, test_metriques, train_y, test_y = train_test_split(X_metriques, y_depots, test_size=0.30,
                                                                        random_state=42)

    # Create a Gaussian Classifier
    clf = RandomForestClassifier(verbose=2, oob_score=True, random_state=42, **kwargs)

    # Train the model using the training sets y_pred=clf.predict(X_test)
    clf.fit(train_metriques, train_y)     # Model fit sur 70%
    y_pred = clf.predict(test_metriques)  # Predicition sur 30%

    # Save the model as a pickle in a file
    if replaceMod is True:
        print(inputEch[-5:])
        joblib.dump(clf, '{}_{}_seg.pkl'.format(outputMod, 'obj'))

    # Impression de précision
    accu_mod = metrics.accuracy_score(test_y, y_pred)
    print("Accuracy:", accu_mod)

    # Génération des graphiques (Appel de fonction)
    indices = []
    if makeplots is True:
        ind_feats = model_plots(test_y=test_y, clf=clf, test_metriques=test_metriques, metriques=metriques)
        indices.append(ind_feats)

    #return clf, plt, accu_mod
    return clf, accu_mod, train_metriques, train_y, test_metriques, test_y

def entrainement_obj_feat(inputEch, outputMod, replaceMod, makeplots, del_liste_feat, **kwargs):
    # Pour importer un shapefile
    # # On crée la liste des shapefiles
    files = os.listdir(inputEch)  # Liste des fichiers dans le dossier "folder"
    shp_list = [os.path.join(inputEch, i) for i in files if i.endswith('.shp')] # Obtenir une liste des chemins pour
                                                                                   # .shp seulement
    # On join les fichiers .shp de la liste
    new_shp_temp = gpd.GeoDataFrame(pd.concat([gpd.read_file(i) for i in shp_list],
                                              ignore_index=True), crs=gpd.read_file(shp_list[0]).crs)

    # On enleve la colonne 'label' et on enleve les rangées 'nulles'
    del_liste_base = ['CorH_media', 'CorH_media', 'CorH_mean', 'CorH_std', 'ANVAD_coun', 'ConH_count', 'CorH_count', 'CVA_count', 'DI_count',
                       'ED_count', 'MeaH_count', 'PC_count', 'Pen_count', 'SSDN_count', 'TPI_count', 'TWI_count']
    print(new_shp_temp.columns)
    new_shp_temp = new_shp_temp.drop(del_liste_base, axis=1)
    print(new_shp_temp.columns)
    new_shp_temp = new_shp_temp.drop(del_liste_feat, axis=1)
    print(new_shp_temp.columns)
    # del new_shp_temp['CorH_media']
    # del new_shp_temp['CorH_mean']
    # del new_shp_temp['CorH_std']
    # del new_shp_temp['ANVAD_coun']
    # del new_shp_temp['ConH_count']
    # del new_shp_temp['CorH_count']
    # del new_shp_temp['CVA_count']
    # del new_shp_temp['DI_count']
    # del new_shp_temp['ED_count']
    # del new_shp_temp['MeaH_count']
    # del new_shp_temp['PC_count']
    # del new_shp_temp['Pen_count']
    # del new_shp_temp['SSDN_count']
    # del new_shp_temp['TPI_count']
    # del new_shp_temp['TWI_count']
    new_shp_temp = new_shp_temp[new_shp_temp.replace([np.inf, -np.inf], np.nan).notnull().all(axis=1)]
    new_shp_temp = new_shp_temp.dropna()
    #new_shp_temp = new_shp_temp.dropna()

    df_majority = new_shp_temp[new_shp_temp.Zone == 0]
    df_minority = new_shp_temp[new_shp_temp.Zone == 1]

    # Downsample majority class
    df_majority_downsampled = resample(df_majority,
                                       replace=False,  # sample without replacement
                                       n_samples=len(df_minority),  # to match minority class
                                       random_state=123)  # reproducible results

    # Combine minority class with downsampled majority class
    new_shp = pd.concat([df_majority_downsampled, df_minority])
    # print(new_shp.columns)
    # print(len(new_shp.columns))

    # On choisi la colonne de que l'on veut prédire (ici le type de dépots)
    y_depots = new_shp.Zone

    # On definit les métriques sur lesquels on veut faire l'analyse
    metriques = list(new_shp.iloc[:, 1:-2])
    # print(metriques)
    # print(len(metriques))
    X_metriques = new_shp[metriques]

    # Séparation des données en données d'entrainement et données de tests
    train_metriques, test_metriques, train_y, test_y = train_test_split(X_metriques, y_depots, test_size=0.30,
                                                                        random_state=42)

    # Create a Gaussian Classifier
    clf = RandomForestClassifier(verbose=2, oob_score=True, random_state=42, **kwargs)

    # Train the model using the training sets y_pred=clf.predict(X_test)
    clf.fit(train_metriques, train_y)     # Model fit sur 70%
    y_pred = clf.predict(test_metriques)  # Predicition sur 30%

    # Save the model as a pickle in a file
    if replaceMod is True:
        print(inputEch[-5:])
        joblib.dump(clf, '{}_{}_seg.pkl'.format(outputMod, 'obj'))

    # Impression de précision
    accu_mod = metrics.accuracy_score(test_y, y_pred)
    print("Accuracy:", accu_mod)

    # Génération des graphiques (Appel de fonction)
    indices = []
    if makeplots is True:
        ind_feats = model_plots(test_y=test_y, clf=clf, test_metriques=test_metriques, metriques=metriques)
        indices.append(ind_feats)

    #return clf, plt, accu_mod
    return clf, accu_mod, train_metriques, train_y, test_metriques, test_y, indices

def HyperTuningGrid(model_base, param_grid, x_train, y_train):
    # Test pour trouver les meilleurs hyperparamètres avec GridSearchCV
    CV_clf = GridSearchCV(estimator=model_base, param_grid=param_grid, cv=5, scoring='accuracy',
                          return_train_score=True)

    modele_opti = CV_clf.fit(x_train, y_train)
    params_opti = CV_clf.best_params_

    ## Results from grid search
    results = CV_clf.cv_results_
    means_test = results['mean_test_score']
    stds_test = results['std_test_score']
    means_train = results['mean_train_score']
    stds_train = results['std_train_score']

    ## Getting indexes of values per hyper-parameter
    masks=[]
    masks_names= list(CV_clf.best_params_.keys())
    for p_k, p_v in CV_clf.best_params_.items():
        masks.append(list(results['param_'+p_k].data==p_v))

    params = CV_clf.param_grid

    ### Optionel pour visualiser les résultats
    # fig, ax = plt.subplots(1,len(params),sharex='none', sharey='all', figsize=(20,5))
    # fig.suptitle('Score per parameter')
    # fig.text(0.04, 0.5, 'Exactitude', va='center', rotation='vertical')
    # pram_preformace_in_best = {}
    # for i, p in enumerate(masks_names):
    #     m = np.stack(masks[:i] + masks[i+1:])
    #     pram_preformace_in_best
    #     best_parms_mask = m.all(axis=0)
    #     best_index = np.where(best_parms_mask)[0]
    #     x = np.array(params[p])
    #     y_1 = np.array(means_test[best_index])
    #     e_1 = np.array(stds_test[best_index])
    #     y_2 = np.array(means_train[best_index])
    #     e_2 = np.array(stds_train[best_index])
    #     ax[i].errorbar(x, y_1, e_1, linestyle='--', marker='o', label='test')
    #     ax[i].errorbar(x, y_2, e_2, linestyle='-', marker='^',label='train')
    #     ax[i].set_xlabel(p.upper())
    #
    # plt.legend()
    # plt.show()

    return modele_opti, params_opti

def plot_valid(param_name, param_range, modele, x_train, y_train):
    train_scores, test_scores = validation_curve(
                                    modele,
                                    X = x_train, y = y_train,
                                    param_name = param_name,
                                    param_range = param_range,
                                    scoring='accuracy',
                                    cv = 5,
                                    verbose=2)

    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    plt.figure()  # Crée une nouvelle instance de graphique
    plt.title("Exactitude en fonction de la valeur de l'hyperparamètre")
    plt.xlabel(param_name)
    plt.xlim([min(param_range), max(param_range)])
    plt.ylabel("Exactitude (%)")
    #plt.ylim(0.65, 0.80)
    plt.ylim(0.70, 0.85)
    #plt.ylim(min(test_scores_mean)-0.05, max(test_scores_mean)+0.05)
    print(test_scores_mean)

    lw = 2

    # plt.semilogx(param_range, train_scores_mean, label="Training score",
    #              color="darkorange", lw=lw)
    # plt.fill_between(param_range, train_scores_mean - train_scores_std,
    #                  train_scores_mean + train_scores_std, alpha=0.2,
    #                  color="darkorange", lw=lw)
    # plt.semilogx(param_range, test_scores_mean, label="Cross-validation score",
    #              color="navy", lw=lw)
    plt.plot(param_range, test_scores_mean, label="Exactitude")
    # plt.fill_between(param_range, test_scores_mean - test_scores_std,
    #                  test_scores_mean + test_scores_std, alpha=0.2,
    #                  color="navy", lw=lw)
    plt.legend(loc="lower right")
    plt.show(block=False)

def classification (num_mod, mod_path, rep_metriques):
    modele_joblib = joblib.load(os.path.join(mod_path, '{}.pkl'.format(num_mod))) # Import du modèle sauvegardé
    tiff_path_list = os.listdir(rep_metriques)  # Liste des fichiers

    # On crée une liste avec toutes les images lues
    tiffs_list = []
    for i in tiff_path_list:
        if i.endswith('.tif'):
            ds = gdal.Open(os.path.join(rep_metriques, i))
            tiffs_list.append(ds.GetRasterBand(1).ReadAsArray())

    # On crée la stack de métrique
    # met_stack = np.stack(tiffs_list)
    met_stack = np.dstack(tiffs_list)

    # On met la stack en 2 dimensions pour pouvoir faire le model dessus
    rows, cols, bands = met_stack.shape
    data2d = np.reshape(met_stack, (rows * cols, bands))

    # Prediction du modèle et on le reshape
    print('Début de la prédiction complète. Cette étape peut prendre plusieurs minutes.')
    prediction = modele_joblib.predict(data2d)
    prediction = np.reshape(prediction, (rows, cols))
    print('Classification terminée.')

    return prediction, tiff_path_list

def classification_obj(seg_num, seg_path, mod_path, mod_num, met_seg, output_path):
    #modele_joblib = joblib.load(os.path.join(mod_path, '{}.pkl'.format(mod_num))) # Import du modèle sauvegardé
    modele_joblib = joblib.load(os.path.join(mod_path, '{}.pkl'.format(mod_num)))  # Import du modèle sauvegardé

    #seg_stats = os.path.join(seg_path, 'seg_stats_{}.shp'.format(seg_num))
    seg_stats = os.path.join(seg_path, '{}.shp'.format(seg_num))

    new_shp_temp = gpd.GeoDataFrame(gpd.read_file(seg_stats))

    # On enleve la colonne 'label' et on enleve les rangées 'nulles'
    del_liste_base = ['CorH_media', 'CorH_media', 'CorH_mean', 'CorH_std', 'ANVAD_coun', 'ConH_count', 'CorH_count', 'CVA_count', 'DI_count',
                      'ED_count', 'MeaH_count', 'PC_count', 'Pen_count', 'SSDN_count', 'TPI_count', 'TWI_count']
    new_shp_temp = new_shp_temp.drop(del_liste_base, axis=1)
    # print(new_shp_temp.columns)
    # new_shp_temp = new_shp_temp.drop(del_liste_feat, axis=1)
    # print(new_shp_temp.columns)

    new_shp_temp = new_shp_temp[new_shp_temp.replace([np.inf, -np.inf], np.nan).notnull().all(axis=1)]
    new_shp_temp = new_shp_temp.dropna()

    #print(new_shp_temp)

    #new_shp_predict = new_shp_temp[met_seg]
    #new_shp_temp = new_shp_temp.drop(met_seg, axis=1)

    # new_shp_predict = new_shp_predict[new_shp_predict.replace([np.inf, -np.inf], np.nan).notnull().all(axis=1)]
    # new_shp_predict = new_shp_predict.dropna()

    #print(new_shp_temp.columns)

    # Prediction du modèle et on le reshape
    print('Début de la prédiction complète. Cette étape peut prendre plusieurs minutes.')
    # new_shp_temp['prediction'] = modele_joblib.predict(data2d)
    # new_shp_temp = np.reshape(prediction, (rows, cols))
    new_shp_temp['prediction'] = modele_joblib.predict(new_shp_temp[met_seg])
    print('Classification terminée.')

    new_shp_temp.to_file(os.path.join(output_path, 'prediction_{}_{}.shp'.format(seg_num, mod_num)))

    return new_shp_temp

def creation_output(prediction, outputdir, nom_fichier, inputMet, tiff_path_list):
    # On crée une image GEOTIFF en sortie
    #logger.info('Création du fichier de sortie {}'.format(os.path.join(outputdir, nom_fichier)))

    print('Enregistrement du raster de sortie')
    # je déclare tous les drivers
    gdal.AllRegister()
    # le driver que je veux utiliser GEOTIFF
    driver = gdal.GetDriverByName("GTiff")

    # taille de mon image (ce sera la taille de la matrice)
    rows, cols = prediction.shape

    # je déclare mon image
    # il faut : la taille, le nombre de bandes et le type de données (ce sera des bytes)
    image = driver.Create((os.path.join(outputdir, nom_fichier)), cols, rows, 1, GDT_Byte)

    # J'extrais les paramètres d'une métriques pour le positionnement du fichier sortant
    data = gdal.Open(os.path.join(inputMet, tiff_path_list[0]))
    geoTransform = data.GetGeoTransform()
    proj = data.GetProjection()
    # nodata = data.GetRasterBand(1).GetNoDataValue()
    data = None # On vide la mémoire

    # Je remets la matrice en 2 dimension
    result1=prediction.reshape(prediction.shape[0], prediction.shape[1])

    # On écrit la matrice dans la bande
    image.GetRasterBand(1).WriteArray(prediction, 0, 0)

    # On donne les paramètres de la métrique à l'image sortante
    image.GetRasterBand(1).SetNoDataValue(255)
    image.SetProjection(proj)
    image.SetGeoTransform(geoTransform)
    image.FlushCache()

    # j'efface ma matrice
    del prediction
    del image

    print('Fin de l\'enregistrement du fichier raster')
    print('...')

    # Impression du temps
    #end = time.time()
    #elapsed = end - start
    #print("Elapsed time : %.2f s" % (elapsed))

def clip_final(path_feuillet, output):
    '''
    :param path_feuillet: No. feuillet avec un buffer à clipper (str)
    :param output: Chemin du fichier de sortie (str)
    :return: Clip du feuillet en entrée clippé à la largeur du feuillet original (.tif)
    '''
    # Chemin du fichier de calssification dans le répertoire racine
    feuillet = os.path.basename(path_feuillet).split('_')[1]

    # Chemin du fichier de référence pour clip dans le répertoire racine
    path_ref = os.path.join(root_dir, 'Backup/MNT_{}_resample.tif'.format(feuillet))

    # Création du cadre pour le clip
    cadre, epsg, nodata = creation_cadre(path_ref)

    # Clip
    clip_raster_to_polygon(path_feuillet, cadre, epsg, 255, output)
    return cadre

    #### FIN SCRIPT ET PROJET GEOINFO ####


def main():
    # Répertoire principal contenant les input et le dossier output pour l'option par défaut
    root_dir = os.path.abspath(os.path.dirname(__file__))

    # Création d'un fichier de log
    config = configparser.ConfigParser()
    print(config.read(os.path.join(root_dir, 'config.ini')))
    logger = logging.getLogger(config.get("Log", "name"))
    # je définis le niveau de log
    logger.setLevel(config.get("Log", "levelfile"))
    # je définis le fichier de log
    fh = logging.FileHandler(config.get("Log", "path"))
    fh.setLevel(config.get("Log", "levelfile"))
    # je définis le log en console
    ch = logging.StreamHandler()
    ch.setLevel(config.get("Log", "levelconsole"))
    # je définis le format du log
    formatter = logging.Formatter('%(levelname)-8s %(asctime)s %(message)s (call: %(module)s-%(funcName)s)')
    # on applique le format au log
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info('Début')
    # erreur1 = "Il manque des arguments. Assurez vous de bien avoir fournie les trois arguments -e -m et -o"
    # inputEch, inputMet, outputdir = "","",""   # Paramètres à fournir par l'utilisateur
    #
    # # Définition et parcours des options
    # opts = None
    # try:
    #     opts, args = getopt.getopt(sys.argv[1:], "hde:m:o:", ["help", "defaultPaths", "inputEchant=","inputMetriques=", "output="])
    #     # print(args)
    #     # print(opts)
    # except getopt.GetoptError as err:
    #     logger.error(erreur1)
    #     print(err)
    #     print("Pour l'aide, utiliser -h ou --help")
    #     sys.exit(2)
    #
    # if len(opts) == 0:                       # On teste d'abord s'il n'y a aucun argument
    #     logger.error(erreur1)
    #     sys.exit(2)
    # elif opts[0][0] in ("-h", "--help"):     # On test si l'utilisateur demande l'aide
    #     print("Cette application vous permet d'appliquer un modèle de prédiction sur un MNT\n"
    #           "Il faut lui fournir le chemin vers vos dossiers d'entraînement, de métrique et de sortie\n"
    #           "Listes des options disponibles en ligne de commande :\n"
    #           "-d ou --defaultPaths     Fournie automatique les données nécessaires pour tester le programme\n"
    #           "-e ou --inputEchant      Spécifier le chemin vers les données d'échantillonage\n"
    #           "-m ou --inputMetriques   Spécifier le chemin vers les données des métriques\n"
    #           "-o ou --output           Spécifier le chemin vers le dossier d'enregistrement")
    #     sys.exit(2)
    # elif opts[0][0] in ("-d", "--defaultPaths"):     # On test si l'utilisateur veut les chemins par défauts
    #     inputEch  = os.path.join(root_dir, 'inputs/inputs_modele_avril2020')
    #     inputMet  = os.path.join(root_dir, 'inputs/tiffs/31H02NE_50m')
    #     outputdir = os.path.join(root_dir, 'outputs/projet_geo_info')
    # elif len(opts) < 3:             # Si l'utilisateur à moins de 3 arguments et n'a pas demandé d'aide
    #     logger.error(erreur1)
    #     sys.exit(2)
    # else:                                            # Si les trois inputs sont entrées, on part le script
    #     for o, a in opts:
    #         if o in ("-e", "--inputEchant"):
    #             inputEch = a
    #         elif o in ("-m", "--inputMetriques"):
    #             inputMet = a
    #         elif o in ("-o", "--output"):
    #             outputdir = a
    #     logger.info('\ninputEch: {}\n'.format(inputEch) + 'inputMet: {}\n'.format(inputMet) + 'outputdir: {}\n'.format(outputdir))

    #### PARAMETRES INITIAUX ####

    # On ajoute la date au fichier sortant pour un meilleur suivi
    date_classi = str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))

    # Structure du nom du fichier sortant
    nom_fichier = 'modele_predit_pixel' + date_classi + '.tiff'

    # # Liste des métriques pour l'analyse
    # # metriques = ['DI', 'MeanHar', 'Pente', 'TPI']
    metriques = ['ANVAD', 'CVA', 'ContHar', 'CorHar', 'DI', 'EdgeDens', 'MeanHar', 'Pente', 'ProfCur', 'TPI', 'SSDN',
                 'TWI']

    ## DÉBUT DES TRAITEMENTS####
    # On démarre le compteur pour cette section
    # Calcul du temps
    logger.info('Metriques choisies: {}'.format(metriques))

    # Import des images en matrices numpy
    tiff_path_list = os.listdir(inputMet)  # Liste des fichiers

    # On crée une liste avec toutes les images lues
    tiffs_list = []
    for i in tiff_path_list:
        if i.endswith('.tif'):
            ds = gdal.Open(os.path.join(inputMet, i))
            tiffs_list.append(ds.GetRasterBand(1).ReadAsArray())

    # Entraînement du modèle
    try:
        logger.info('Entrainement...')
        ent = entrainement(inputEch=inputEch, metriques=metriques)
    except Exception as e:
        logger.error("Erreur dans l'entrainement du modèle: \n{}".format(e))
        sys.exit()

    # Classification selon les métriques
    try:
        logger.info('Classification...')
        classif = classification(clf=ent, tiffs_list=tiffs_list)
    except Exception as e:
        logger.error("Erreur dans la classification: \n{}".format(e))
        sys.exit()

    # Création du fichier de sortie
    try:
        creation_output(prediction=classif, outputdir=outputdir , nom_fichier=nom_fichier,
                        inputMet=inputMet, tiff_path_list=tiff_path_list, start=start, logger=logger)
    except Exception as e:
        logger.error("Erreur dans la création du fichier de sortie: \n{}".format(e))
        sys.exit()

    logger.info('Terminé')





if __name__ == "__main__":
    main()