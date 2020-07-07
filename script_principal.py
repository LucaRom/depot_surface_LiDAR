from Download_MNT import download_mnt
from pretraitements import pretraitements
from production_metriques import creation_metriques
from ech_pixel import echantillonnage_pix
from fonctions_modele import entrainement_pix, entrainement_obj, entrainement_obj_feat, classification, \
    classification_obj, creation_output, HyperTuningGrid, plot_valid
from ech_objet import echantillonnage_obj
import os
import matplotlib.pyplot as plt
from osgeo import gdal
import statistics

# Définition du chemin racine du dossier de travail
root_dir = os.path.abspath(os.path.dirname(__file__))
path_r = r"E:\Program Files\R\R-3.6.1\bin\Rscript.exe"  # Chemin vers l'application 'Rscript.exe' de l'ordinateur

# Données initiales à changer par l'utilisateur
# liste_feuillet = ['32D06NE', '32D06SE']  # Entrée la liste des feuillets désiré, n'en mettre qu'un seul pour un feuillet.


#### SECTION 1 - Production des métriques ####
'''
Cette section crée des fichiers pour chaque métriques définies

Dans l'ordre, le code : 1) Télécharge le MNT du feuillet ciblé ainsi que tous les MNT adjacents
                        2) Crée une zone tampon autour du feuillet ciblé
                        3) Produit les métriques en appelant le fichier 'production_metriques.py'
                        
Fichiers produits : Fichier .tif par métrique dans le dossier './inputs/tiffs/no_du_feuillet/'

NOTES : 1) Le processus peut se faire en boucle sur plusieurs feuillets (ex.: dans le cas qu'on voudrait échantilloner sur
           plus d'un feuillet.
           
        2) La fonction nécessite d'appeler "R" pour créer les métriques d'Haralick. Il faut spécifier le chemin de "R" 
           sur l'ordinateur que vous utilisez. Voir la variable "path_script" dans la fonction.
       
'''

def mnt_metriques(liste_feuillet, creation):
    """
    :param liste_feuillet: Spécifier une liste (ex. liste = [31h02SO, 31H02SE, 31H02NE]) pour créer les métriques sur un
                           ou plusieurs feuillets.

    :param creation: Spécifier si la fonction doit créer ou non les fichiers de métriques (utile si appeler dans une autre
                    fonction).
    """

    rep_metriques = None
    rep_mnt_buff = None
    for i in liste_feuillet:
        feuillet = i

        ftpdirectory = 'transfert.mffp.gouv.qc.ca'  # site ftp
        ftpparent = r'Public/Diffusion/DonneeGratuite/Foret/IMAGERIE/Produits_derives_LiDAR/'  # répertoire de base
        path_index = os.path.join(root_dir, 'inputs/MNT/index/Index_ProduitsDerive_LiDAR_Sweb.shp')
        col_feuillet = 'FCA_NO_FEU'  # colonne des numéro de feuillet dans la couche index
        rep_mnt = os.path.join(root_dir, 'inputs/MNT/originaux')  # Répertoire contenant les MNT téléchargés

        # Intrants pour les prétraitements
        distance_buffer = 1000  # Distance pour le buffer autour du raster
        size_resamp = 5  # Taille de rééchantillonnage
        rep_mnt_buff = os.path.join(root_dir, 'inputs/MNT/buffer')  # Chemin des fichiers temporaires rééchantillonnés

        # Intrants pour la production de métriques
        rep_metriques = os.path.join(root_dir, 'inputs/tiffs',
                                     feuillet)  # Chemin vers le répertoire output des métriques
        mntbuff = os.path.join(rep_mnt_buff, feuillet[:-2], '{}_buffer.tif'.format(feuillet))
        path_script = os.path.join(root_dir, 'inputs/scripts/haralick.R')  # Chemin vers le script 'haralick.R'

        if creation is True:
            # Appel des fonctions externes
            # Téléchargement des MNT si nécessaire
            mnts = download_mnt(feuillet=feuillet, path_index=path_index, col_feuillet=col_feuillet,
                                ftpparent=ftpparent, ftpdirectory=ftpdirectory, output=rep_mnt)
            # Prétraitements
            pretraitements(feuillet=feuillet, liste_path_feuillets=mnts, distance_buffer=distance_buffer,
                           size_resamp=size_resamp, rep_output=rep_mnt_buff)

            # # Création des métriques
            creation_metriques(mnt=mntbuff, feuillet=feuillet, rep_output=rep_metriques, path_r=path_r, path_script=path_script)

    return rep_metriques, rep_mnt_buff


#### SECTION 2a - Échantillonage pixel et objet ####
'''
À REMPLIR
'''


def echant_main(liste_feuillet, creation, approche):
    rep_metriques, rep_mnt_buff = mnt_metriques(liste_feuillet, creation)  # Appel de variables de la SECTION 1
    for i in liste_feuillet:
        feuillet = i

        # Intrants communs aux deux approches
        path_depot = os.path.join(root_dir, 'inputs/depots', feuillet, 'zones_depots_glaciolacustres_{}.shp'.format(
            feuillet))  # Chemins des couches du MNT et de la couche de dépôts
        path_mnt = os.path.join(root_dir, 'inputs/MNT/resample', feuillet[:-2], 'MNT_{}_resample.tif'.format(feuillet))

        if approche == 'pixel':
            # Intrants pour l'échantillonnage par pixel
            echant = os.path.join(root_dir, 'inputs/ech_entrainement_mod/pixel', feuillet[:-2],
                                  'ech_{}.shp'.format(feuillet))

            # Échantillonnage par pixel
            echantillonnage_pix(path_depot=path_depot, path_mnt=path_mnt, path_metriques=rep_metriques,
                                output=echant, nbPoints=2000, minDistance=500)
        elif approche == 'objet':
            # Intrant pour l'échantillonnage par objet
            path_segmentation = os.path.join(root_dir, 'inputs/segmentations', 'seg_{}.shp'.format(feuillet))
            output = os.path.join(root_dir, 'inputs/ech_entrainement_mod/objet', feuillet[:-2],
                                  'segmentation_{}.shp'.format(feuillet))

            # Échantillonnage par objet
            echantillonnage_obj(path_metriques=rep_metriques, path_met_cadre=path_mnt,
                                path_segmentation=path_segmentation,
                                output=output, path_depot=path_depot)

        # Cette section n'inclut pas un "path_depot" quand on appelle la fonction "echantillonage_obj" ce qui ne crée
        # pas de fichier d'entrainement.
        elif approche == 'objet2':
            # Intrant pour l'échantillonnage par objet
            path_segmentation = os.path.join(root_dir, 'inputs/segmentations', 'seg_{}.shp'.format(feuillet))
            output = os.path.join(root_dir, 'inputs/segmentations/stats_zonales', feuillet[:-2],
                                  'seg_stats_{}.shp'.format(feuillet))

            # Échantillonnage par objet
            echantillonnage_obj(path_metriques=rep_metriques, path_met_cadre=path_mnt,
                                path_segmentation=path_segmentation,
                                output=output)


# liste_feuillet = ['31H02SE']
# echant_main(liste_feuillet, creation=False, approche='objet')


#### SECTION 3a - (OPTIONNEL) Optimisation/recherche des hyperparamètres ####
'''
Cette section contient la fonction qui recherche les paramètres optimaux pour l'entraînement du modèle

Dans l'ordre, le code : 1) Télécharge le MNT du feuillet ciblé ainsi que tous les MNT adjacents
                        2) Crée une zone tampon autour du feuillet ciblé
                        3) Produit les métriques en appelant le fichier 'production_metriques.py'

Fichiers produits : Fichier .tif par métrique dans le dossier './inputs/tiffs/no_du_feuillet/'

NOTE : #### ATTENTION CE PROCESSUS PEUT ÊTRE TRÈS LONG !!! ####

'''

'''
Cette section crée des fichiers pour chaque métriques définies

Dans l'ordre, le code : 1) Télécharge le MNT du feuillet ciblé ainsi que tous les MNT adjacents
                        2) Crée une zone tampon autour du feuillet ciblé
                        3) Produit les métriques en appelant le fichier 'production_metriques.py'

Fichiers produits : Fichier .tif par métrique dans le dossier './inputs/tiffs/no_du_feuillet/'

NOTES : 1) Le processus peut se faire en boucle sur plusieurs feuillets (ex.: dans le cas qu'on voudrait échantilloner sur
           plus d'un feuillet.

        2) La fonction nécessite d'appeler "R" pour créer les métriques d'Haralick. Il faut spécifier le chemin de "R" 
           sur l'ordinateur que vous utilisez. Voir la variable "path_script" dans la fonction.

'''



def gridSearch_params_opti(inputEch, metriques_pixel, outputMod):
    # Intrants pour l'optimisation des hyperparamètres du modele
    # Grille de paramètre pour le GridSearchCV
    param_grid = {
        "n_estimators": [200, 500, 800, 1000, 5000, 10000],
        "max_features": ['auto', 'sqrt', 'log2'],
        "max_depth": [None, 2, 4, 6, 8, 10]
    }
    # Création du modèle de base
    params_base = {'n_estimators': 200}
    clf, accu_mod, train_metriques, train_y, test_metriques, test_y = entrainement_pix(inputEch=inputEch,
                                                                                       metriques=metriques_pixel,
                                                                                       outputMod=outputMod,
                                                                                       replaceMod=False,
                                                                                       makeplots=False, **params_base)
    # Modele d'optimisation avec GridSearchCV
    modele_opti, params_opti = HyperTuningGrid(model_base=clf, param_grid=param_grid, x_train=train_metriques,
                                               y_train=train_y)
    print(params_opti)  # Impression des meilleurs résultats basé sur param_grid

    return params_opti


# # Impression des courbes de validation pour chaque hyperparamètre
# for key, value in param_grid.items():  # Pour chaque items de la liste des paramètres à optimiser
#     plot_valid(param_name=key, param_range=value, modele=clf, x_train=train_metriques, y_train=train_y)

def vali_plots_pix(feuillet):
    # # Intrants pour l'entraînement du modele
    # metriques_pixel = ['ANVAD', 'ConH', 'CorH', 'CVA', 'DI', 'ED', 'MeaH', 'PC', 'Pen', 'SSDN', 'TPI', 'TWI']
    metriques_pixel = ['ANVAD', 'ConH', 'CorH', 'CVA', 'DI', 'ED', 'MeaH', 'PC', 'Pen', 'SSDN', 'TPI', 'TWI']
    inputEch = os.path.join(os.path.join(root_dir, 'inputs/ech_entrainement_mod/pixel/', feuillet[:-2]))
    # inputEch = os.path.join(os.path.join(root_dir, 'inputs/ech_entrainement_mod/pixel/', '{}_no_anth'.format(feuillet[:-2])))
    outputMod = os.path.join(os.path.join(root_dir, 'inputs/modeles', feuillet[-7:-2]))
    # outputMod = os.path.join(os.path.join(root_dir, 'inputs/modeles', '{}_no_anth'.format(feuillet[-7:-2])))

    param_grid = {
        "n_estimators": [200, 500, 800, 1000, 5000, 10000],
        "max_features": ['auto', 'sqrt', 'log2'],
        "max_depth": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    }
    # Création du modèle de base
    params_base = {'n_estimators': 1000}
    clf, accu_mod, train_metriques, train_y, test_metriques, test_y = entrainement_pix(inputEch=inputEch,
                                                                                       metriques=metriques_pixel,
                                                                                       outputMod=outputMod,
                                                                                       replaceMod=False,
                                                                                       makeplots=False, **params_base)

    # # Impression des courbes de validation pour chaque hyperparamètre

    # param_range.append()
    # param_range.append(None)

    param_range = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    plot_valid(param_name='n_estimators', param_range=param_range, modele=clf, x_train=train_metriques, y_train=train_y)

    # param_range = [200, 500, 800, 1000, 5000, 10000]
    # plot_valid(param_name='n_estimators', param_range=param_range, modele=clf, x_train=train_metriques, y_train=train_y)

    # param_range = ['auto', 'sqrt', 'log2']
    # plot_valid(param_name='max_features', param_range=param_range, modele=clf, x_train=train_metriques, y_train=train_y)


# vali_plots('31H02NE')

def vali_plots_obj(feuillet):
    # # Intrants pour l'entraînement du modele
    # # Intrants pour l'entraînement du modele
    inputEch = os.path.join(os.path.join(root_dir, 'inputs/ech_entrainement_mod/objet/', feuillet[:-2]))
    outputMod = os.path.join(os.path.join(root_dir, 'inputs/modeles', feuillet[-10:-3]))

    param_grid = {
        "n_estimators": [200, 500, 800, 1000, 5000, 10000],
        "max_features": ['auto', 'sqrt', 'log2'],
        "max_depth": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    }
    # Création du modèle de base
    params_base = {'n_estimators': 1000}
    clf, accu_mod, train_metriques, train_y, test_metriques, test_y = entrainement_obj(inputEch=inputEch,
                                                                                       outputMod=outputMod,
                                                                                       replaceMod=False, makeplots=True,
                                                                                       **params_base)

    # # Impression des courbes de validation pour chaque hyperparamètre

    # param_range.append()
    # param_range.append(None)

    # param_range = [200, 500, 800, 1000, 5000, 10000]
    # plot_valid(param_name='n_estimators', param_range=param_range, modele=clf, x_train=train_metriques, y_train=train_y)

    # param_range = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    param_range = list(range(2, 21))
    plot_valid(param_name='max_depth', param_range=param_range, modele=clf, x_train=train_metriques, y_train=train_y)

    # param_range = ['auto', 'sqrt', 'log2']
    # plot_valid(param_name='max_features', param_range=param_range, modele=clf, x_train=train_metriques, y_train=train_y)


# del_liste_feat = []
# for i in range(0,1):
# del_liste_feat = []

# vali_plots_obj('32D01NO')
# vali_plots_obj('31H02NE')

#### SECTION 4a - Entraînement du modèle par pixel  ####
'''
À REMPLIR
avec matrice de confusion et importance des métriques
'''


def entrain_main_pix(feuillet, opti=False, makeplots=False, replaceMod=False):
    # # Intrants pour l'entraînement du modele
    # metriques_pixel = ['MeaH']
    metriques_pixel = ['ANVAD', 'ConH', 'CorH', 'CVA', 'DI', 'ED', 'MeaH', 'PC', 'Pen', 'SSDN', 'TPI', 'TWI']
    #inputEch = os.path.join(os.path.join(root_dir, 'inputs/ech_entrainement_mod/pixel/', feuillet[:-2]))
    inputEch = os.path.join(os.path.join(root_dir, 'inputs/ech_entrainement_mod/pixel/', '31H02_32D01'))
    #outputMod = os.path.join(os.path.join(root_dir, 'inputs/modeles', feuillet[-7:-2]))
    outputMod = os.path.join(os.path.join(root_dir, 'inputs/modeles', '31H02_32D01'))
    # outputMod = os.path.join(os.path.join(root_dir, 'inputs/modeles', '{}_no_anth'.format(feuillet[-7:-2])))

    if opti is True:
        print('Début de GridSearchCV pour trouver les paramètres optimaux')
        params_opti = gridSearch_params_opti(inputEch=inputEch, metriques_pixel=metriques_pixel, outputMod=outputMod)
        print('Fin du GridSearchCV')
    elif opti == '31H02':
        print('Début de l\'entrainement avec les paramètres optimisé pour la zone 31H02')
        # params_opti = {'max_depth': 4, 'max_features': 'auto', 'n_estimators': 1000}
        params_opti = {'max_depth': 7, 'max_features': 'auto', 'n_estimators': 1000}
    elif opti == '32D01':
        print('Début de l\'entrainement avec les paramètres optimisé pour la zone 32D01')
        params_opti = {'max_depth': 4, 'max_features': 'auto', 'n_estimators': 5000}
    else:
        # Utilise les paramètres optimisés issues de l'étape optimisation
        #params_opti = {'max_depth': None, 'max_features': 'auto', 'n_estimators': 200}
        params_opti = {'max_depth': None, 'max_features': 'auto', 'n_estimators': 1000}

    print('Début de l\'entrainement du modèle')
    clf, accu_mod, train_metriques, train_y, test_metriques, test_y = entrainement_pix(inputEch=inputEch,
                                                                                       metriques=metriques_pixel,
                                                                                       outputMod=outputMod,
                                                                                       replaceMod=replaceMod,
                                                                                       makeplots=makeplots,
                                                                                       **params_opti)
    print('Fin de l\'entrainement du modèle en utilisant les paramètres :')
    print(params_opti)

    return clf, accu_mod, params_opti, train_metriques, train_metriques, test_metriques, test_y

#entrain_main_pix('31H02_32D01_1', opti=False, makeplots=True, replaceMod=True)

def entrain_main_obj(feuillet, opti=False, makeplots=False, replaceMod=False):
    # # Intrants pour l'entraînement du modele
    inputEch = os.path.join(os.path.join(root_dir, 'inputs/ech_entrainement_mod/objet/', feuillet[:-2]))
    outputMod = os.path.join(os.path.join(root_dir, 'inputs/modeles', feuillet[-10:-3]))

    print(inputEch)

    # inputEch = os.path.join(os.path.join(root_dir, 'inputs/segmentations/remise/'))
    # outputMod = os.path.join(os.path.join(root_dir, 'inputs/segmentations/remise/'))

    ######entrainement_obj(inputEch, outputMod, replaceMod, makeplots, **kwargs)

    if opti is True:
        print('Début de GridSearchCV pour trouver les paramètres optimaux')
        params_opti = gridSearch_params_opti(inputEch=inputEch, metriques_pixel=metriques_pixel, outputMod=outputMod)
        print('Fin du GridSearchCV')
    elif opti == '31H02':
        print('Début de l\'entrainement avec les paramètres optimisé pour la zone 31H02')
        params_opti = {'max_depth': 12, 'max_features': 'auto', 'n_estimators': 1000}
    elif opti == '32D01':
        print('Début de l\'entrainement avec les paramètres optimisé pour la zone 32D01')
        params_opti = {'max_depth': 12, 'max_features': 'auto', 'n_estimators': 1000}
    else:
        # Utilise les paramètres optimisés issues de l'étape optimisation
        params_opti = {'max_depth': None, 'max_features': 'auto', 'n_estimators': 200}

    print(params_opti)
    print('Début de l\'entrainement du modèle')
    clf, accu_mod, train_metriques, train_y, test_metriques, test_y = entrainement_obj(inputEch=inputEch,
                                                                                       outputMod=outputMod,
                                                                                       replaceMod=replaceMod,
                                                                                       makeplots=makeplots,
                                                                                       **params_opti)

    print('Fin de l\'entrainement du modèle en utilisant les paramètres :')
    print(params_opti)

    return clf, accu_mod, params_opti, train_metriques, train_metriques, test_metriques, test_y


# entrain_main_obj('31H02NE', opti='31H02', makeplots=True, replaceMod=True)
# entrain_main_obj('32D01NO', opti='32D01', makeplots=True, replaceMod=True)

def entrain_main_obj_feats(feuillet, del_liste_feat, opti=False, makeplots=False, replaceMod=False):
    # # Intrants pour l'entraînement du modele
    inputEch = os.path.join(os.path.join(root_dir, 'inputs/ech_entrainement_mod/objet/', feuillet[:-2]))
    outputMod = os.path.join(os.path.join(root_dir, 'inputs/modeles', feuillet[-7:-2]))

    ######entrainement_obj(inputEch, outputMod, replaceMod, makeplots, **kwargs)

    if opti is True:
        print('Début de GridSearchCV pour trouver les paramètres optimaux')
        params_opti = gridSearch_params_opti(inputEch=inputEch, metriques_pixel=metriques_pixel, outputMod=outputMod)
        print('Fin du GridSearchCV')
    elif opti == '31H02':
        print('Début de l\'entrainement avec les paramètres optimisé pour la zone 31H02')
        params_opti = {'max_depth': 12, 'max_features': 'auto', 'n_estimators': 1000}
    elif opti == '32D01':
        print('Début de l\'entrainement avec les paramètres optimisé pour la zone 32D01')
        params_opti = {'max_depth': 12, 'max_features': 'auto', 'n_estimators': 1000}
    else:
        # Utilise les paramètres optimisés issues de l'étape optimisation
        params_opti = {'max_depth': None, 'max_features': 'auto', 'n_estimators': 200}

    print('Début de l\'entrainement du modèle')
    # clf, accu_mod, train_metriques, train_y, test_metriques, test_y = entrainement_obj(inputEch=inputEch, outputMod=outputMod,
    #                                                                                    replaceMod=replaceMod, makeplots=makeplots,
    #                                                                                    **params_opti)

    # Pour features selections
    clf, accu_mod, train_metriques, train_y, test_metriques, test_y, indices = entrainement_obj_feat(inputEch=inputEch,
                                                                                                     outputMod=outputMod,
                                                                                                     replaceMod=replaceMod,
                                                                                                     makeplots=makeplots,
                                                                                                     del_liste_feat=del_liste_feat,
                                                                                                     **params_opti)
    print('Fin de l\'entrainement du modèle en utilisant les paramètres :')
    print(params_opti)

    return clf, accu_mod, params_opti, train_metriques, train_metriques, test_metriques, test_y, indices


# # Pour calculer l'impact d'enlever les métriques sans les faire une par une
# # # Sort deux listes
# del_liste_feat = []
# del_liste_feat = []
# accu_mod_liste = []
# for i in range(0,58):
#     clf, accu_mod, params_opti, train_metriques, train_metriques, test_metriques, test_y, indices = entrain_main_obj_feats('32D01NO', del_liste_feat=del_liste_feat, opti='32D01', makeplots=True, replaceMod=False)
#     print(indices)
#     print(indices[0][0])
#     del_liste_feat.append(indices[0][0])
#     print(accu_mod)
#     accu_mod_liste.append(accu_mod)
#     print(accu_mod_liste)
#     print(del_liste_feat)

# del_liste_feat = ['ConH_min', 'CorH_min', 'ConH_media', 'ANVAD_medi', 'ED_min', 'Pen_max', 'PC_mean', 'ConH_max', 'ED_median', 'ANVAD_mean', 'ConH_mean', 'PC_min', 'SSDN_media', 'PC_max', 'DI_min', 'TPI_max', 'PC_median', 'SSDN_min', 'ConH_std', 'Pen_min', 'Pen_mean', 'TWI_mean', 'ANVAD_max', 'ANVAD_std', 'TWI_min', 'SSDN_mean', 'ED_max', 'CVA_mean', 'Pen_std', 'TWI_std', 'DI_max', 'ED_mean', 'TPI_mean']
# entrain_main_obj_feats('31H02NE', del_liste_feat=del_liste_feat, opti='31H02', makeplots=True, replaceMod=True)

# for i in liste_feuillet:
#     echant_main(liste_feuillet, creation=False)

# accuracy_list = []
# for i in range(10):
#     clf, accu_mod, train_metriques, train_y, test_metriques, test_y =  entrain_main(liste_feuillet[0])
#     accuracy_list.append(accu_mod)
#
# print(accuracy_list)
# print(statistics.mean(accuracy_list))
# # #
#

# def entrain_accu_moyenne_super_loop():
#     for i in range(10):
#         clf, accu_mod = entrainement(inputEch=inputEch, metriques=metriques_pixel)
#         accuracy_list.append(accu_mod)
#     return clf, accuracy_list

# clf, accuracy_list = entrain_accu_moyenne_super_loop()
# print(accuracy_list)
# print(statistics.mean(accuracy_list))


#### SECTION 5a - Classification par pixel ####
'''
À REMPLIR
'''


def class_main(feuillet, num_mod):
    # # Intrants pour la classification du modèle
    mod_path = os.path.join(root_dir, 'inputs/modeles')  # Chemin vers le dossier des modèles
    rep_metriques = os.path.join(root_dir, 'inputs/tiffs', feuillet)  # Chemin vers le dossier des métriques
    nom_fichier = 'prediction_{}_{}.tif'.format(feuillet, num_mod)  # Nom du fichier à sauvegarder
    outputdir = os.path.join(root_dir, 'outputs/pixel')  # Dossier output du .shp prédit

    # Classification avec le modèle et création du fichier résultant
    classif, tiff_path_list = classification(num_mod=num_mod, mod_path=mod_path, rep_metriques=rep_metriques)
    creation_output(prediction=classif, outputdir=outputdir, nom_fichier=nom_fichier,
                    inputMet=rep_metriques, tiff_path_list=tiff_path_list)


# def class_main_obj(feuillet, num_mod):

# Pour importer un shapefile
# # On crée la liste des shapefiles
# files = os.listdir(inputEch)  # Liste des fichiers dans le dossier "folder"
# shp_list = [os.path.join(inputEch, i) for i in files if i.endswith('.shp')] # Obtenir une liste des chemins pour
# .shp seulement

# On join les fichiers .shp de la liste
# new_shp_temp = gpd.GeoDataFrame(pd.concat([gpd.read_file(i) for i in shp_list],
#                                           ignore_index=True), crs=gpd.read_file(shp_list[0]).crs)
#
# import geopandas as gpd
# import numpy as np
#
# i = r'E:\OneDrive - USherbrooke\001 APP\Programmation\inputs\segmentations\stats_zonales\seg_stats_31H02SO.shp'
# #new_shp_temp = gpd.GeoDataFrame(gpd.read_file(i) , ignore_index=True)
#
# new_shp_temp = gpd.GeoDataFrame(gpd.read_file(i))
# met_seg = ['CVA_median', 'SSDN_max', 'ANVAD_medi', 'DI_median', 'Pen_median', 'CVA_min', 'DI_mean', 'ANVAD_max', 'DI_max', 'Pen_mean', 'MeaH_media', 'Pen_max', 'MeaH_max', 'MeaH_mean']

# # Prediction complète
# clf, accu_mod, params_opti, train_metriques, train_metriques, test_metriques, test_y = entrain_main_obj('31H02NE', opti='31H02', makeplots=True, replaceMod=True)
#
# new_shp_temp = new_shp_temp[met_seg]
#
# new_shp_temp = new_shp_temp[new_shp_temp.replace([np.inf, -np.inf], np.nan).notnull().all(axis=1)]
# new_shp_temp = new_shp_temp.dropna()
#
# new_shp_temp['prediction'] = clf.predict(new_shp_temp)

# ICI ICI
# seg_path = os.path.join(root_dir, 'inputs/segmentations/stats_zonales/31H02')
# # mod_path = os.path.join(root_dir, 'inputs/modeles')
# # output_path =  os.path.join(root_dir, 'outputs/objet')


# met_seg = ['CorH_max', 'CVA_median', 'SSDN_max', 'ANVAD_medi', 'DI_median', 'Pen_median', 'CVA_min', 'DI_mean', 'ANVAD_max', 'DI_max', 'Pen_mean', 'MeaH_media', 'Pen_max', 'MeaH_max', 'MeaH_mean']
# met_seg = ['ConH_min', 'CorH_min', 'ED_min', 'ConH_media', 'ConH_max', 'ConH_std', 'ConH_mean', 'ED_std', 'DI_min', 'TPI_std', 'ANVAD_std', 'CVA_std', 'TWI_max', 'TWI_std', 'SSDN_mean', 'TWI_median', 'ED_median', 'SSDN_media', 'CVA_max', 'PC_median', 'TPI_max', 'ED_mean', 'TWI_mean', 'SSDN_std', 'PC_max', 'SSDN_min', 'PC_min', 'ANVAD_min', 'DI_std', 'TPI_mean', 'TWI_min', 'PC_mean', 'ANVAD_mean', 'CVA_mean', 'Pen_min', 'PC_std', 'MeaH_std', 'ED_max', 'TPI_median', 'Pen_std', 'TPI_min']
# met_seg = ['ANVAD_min', 'ANVAD_max', 'ANVAD_medi', 'ANVAD_mean',
#        'ANVAD_std', 'ConH_min', 'ConH_max', 'ConH_media', 'ConH_mean',
#        'ConH_std', 'CorH_min', 'CorH_max', 'CVA_min', 'CVA_max', 'CVA_median',
#        'CVA_mean', 'CVA_std', 'DI_min', 'DI_max', 'DI_median', 'DI_mean',
#        'DI_std', 'ED_min', 'ED_max', 'ED_median', 'ED_mean', 'ED_std',
#        'MeaH_min', 'MeaH_max', 'MeaH_media', 'MeaH_mean', 'MeaH_std', 'PC_min',
#        'PC_max', 'PC_median', 'PC_mean', 'PC_std', 'Pen_min', 'Pen_max',
#        'Pen_median', 'Pen_mean', 'Pen_std', 'SSDN_min', 'SSDN_max',
#        'SSDN_media', 'SSDN_mean', 'SSDN_std', 'TPI_min', 'TPI_max',
#        'TPI_median', 'TPI_mean', 'TPI_std', 'TWI_min', 'TWI_max', 'TWI_median',
#        'TWI_mean', 'TWI_std']

### met_seg pour 31H02 ###
met_seg = ['ANVAD_min', 'CorH_max', 'CVA_min', 'CVA_max', 'CVA_median',
           'CVA_std', 'DI_median', 'DI_mean', 'DI_std', 'ED_std', 'MeaH_min',
           'MeaH_max', 'MeaH_media', 'MeaH_mean', 'MeaH_std', 'PC_std',
           'Pen_median', 'SSDN_max', 'SSDN_std', 'TPI_min', 'TPI_median',
           'TPI_std', 'TWI_max', 'TWI_median']

### TOUTES LES MÉTRIQUES pour modèle 32D01 ####
# met_seg = ['ANVAD_min', 'ANVAD_max', 'ANVAD_medi', 'ANVAD_mean',
#        'ANVAD_std', 'ConH_min', 'ConH_max', 'ConH_media', 'ConH_mean',
#        'ConH_std', 'CorH_min', 'CorH_max', 'CVA_min', 'CVA_max', 'CVA_median',
#        'CVA_mean', 'CVA_std', 'DI_min', 'DI_max', 'DI_median', 'DI_mean',
#        'DI_std', 'ED_min', 'ED_max', 'ED_median', 'ED_mean', 'ED_std',
#        'MeaH_min', 'MeaH_max', 'MeaH_media', 'MeaH_mean', 'MeaH_std', 'PC_min',
#        'PC_max', 'PC_median', 'PC_mean', 'PC_std', 'Pen_min', 'Pen_max',
#        'Pen_median', 'Pen_mean', 'Pen_std', 'SSDN_min', 'SSDN_max',
#        'SSDN_media', 'SSDN_mean', 'SSDN_std', 'TPI_min', 'TPI_max',
#        'TPI_median', 'TPI_mean', 'TPI_std', 'TWI_min', 'TWI_max', 'TWI_median',
#        'TWI_mean', 'TWI_std']

# seg_path = os.path.join(root_dir, 'inputs/segmentations')
# mod_path = os.path.join(root_dir, 'inputs/modeles')
# output_path =  os.path.join(root_dir, 'outputs/objet')
#
# classification_obj(seg_num='seg_stats_31H02SE_v2', seg_path=seg_path, mod_path=mod_path, mod_num='31H02_obj_seg', met_seg=met_seg, output_path=output_path)

# seg_path = os.path.join(root_dir, 'inputs/segmentations')
# mod_path = os.path.join(root_dir, 'inputs/modeles')
# output_path =  os.path.join(root_dir, 'outputs/objet')
#
# classification_obj(seg_num='seg_stats_32D02SE_v2', seg_path=seg_path, mod_path=mod_path, mod_num='31H02_obj_seg', met_seg=met_seg, output_path=output_path)
#

#### SECTION 6 - Exemple d'utilisation ####
'''
1. Fonction 'echant_main(liste_feuillet, creation)'
    - Création des métriques et de l'échantillonage pour entrainter le modèle
    - Si les métriques ont déjà été produites, mettre le paramètre "creation" à 'false pour ne créer que les 
      échantillonages
    - Le paramètre 'creation' appelle la fonction 'mnt_metriques(liste_feuillet, creation)' qui pourrait être utilisée
      seule si désirée. Mais nous conseillons de toujours l'utiliser avec l'échantillonage pour éviter les erreurs/confusions.

2.  Fonction 'entrain_main(feuillet, opti=False)'
    - Creation du modèle 


À compléter
'''

#### EXEMPLE D'UTILISATION DE LA FONCTION DE CRÉATION DES MÉTRIQUES (SECTION 1)

#liste_feuillet = ['32D02SE']
#mnt_metriques(liste_feuillet=liste_feuillet, creation=True)


# # Commencer par déterminer les feuillets que l'on désire traiter
# liste_feuillet = ['32D01NO', '32D01']
#
# echant_main(liste_feuillet, creation=True, approche='objet')
#

# Entrainement du modèle
# entrain_main_pix('31H02NE', '31H02', makeplots=True, replaceMod=True)
# entrain_main('31H02NE', '31H02', makeplots=True, replaceMod=False)

# Classification d'un feuillet
class_main(feuillet='31H02SO', num_mod='31H02_32D01')
class_main(feuillet='32D02SE', num_mod='31H02_32D01')
# class_main(feuillet='32D02SE', num_mod='31H02_no_anth_no_anth')
# class_main(feuillet='31H02SO', num_mod='32D01')
# class_main(feuillet='32D02SE', num_mod='32D01')

#class_main(feuillet='31H02SE', num_mod='32D01')

#### A REVOIR???? ####
# # Suppression des fichiers
# # for files in os.listdir(rep_mnt_buff):
# #     path = os.path.join(rep_mnt_buff, files)
# #     if os.path.isdir(path) is False:
# #         os.remove(path)
#
# # # À mettre à la fin d'entrainement modèle
# #print('Fin de l\'entrainement, veuillez fermer les graphiques pour continuer')
# # print('Les paramètres optimaux sont : ')
# # print(params_opti)
# print('Fin du script, veuillez fermer les graphiques pour terminer')
# #plt.show() # Garder les graphiques ouverts jusqu'à la fin si nécessaire
#
# # Échnatillonage
# # liste_feuillet : [] #liste des feuillets (mettre un seul si un seul, mais laisser une liste
# #
# # for i in liste_feuillet:
# #     fonct_echnatill
#
#
# # Classements
# liste_feuillet : []