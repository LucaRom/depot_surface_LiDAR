from Download_MNT import download_mnt
from pretraitements import pretraitements
from production_metriques import creation_metriques
from ech_pixel import echantillonnage_pix
from fonctions_modele import entrainement, classification, creation_output, HyperTuningGrid, plot_valid

import os
import matplotlib.pyplot as plt
from osgeo import gdal
import statistics

# Définition du chemin racine du dossier de travail
root_dir = os.path.abspath(os.path.dirname(__file__))
path_r = r"E:\Program Files\R\R-3.6.1\bin\Rscript.exe"  # Chemin vers l'application 'Rscript.exe' de l'ordinateur

# Données initiales à changer par l'utilisateur
#liste_feuillet = ['32D06NE', '32D06SE']  # Entrée la liste des feuillets désiré, n'en mettre qu'un seul pour un feuillet.


#### SECTION 1 - Production des métriques ####
'''
Cette section crée des fichiers pour chaque métriques définies

Dans l'ordre, le code : 1) Télécharge le MNT du feuillet ciblé ainsi que tous les MNT adjacents
                        2) Crée une zone tampon autour du feuillet ciblé
                        3) Produit les métriques en appelant le fichier 'production_metriques.py'
                
Fichiers produits : Fichier .tif par métrique dans le dossier './inputs/tiffs/no_du_feuillet/'
                        
NOTE : Le processus peut se faire en boucle sur plusieurs feuillets (ex.: dans le cas qu'on voudrait échantilloner sur
       plus d'un feuillet.
'''

def mnt_metriques(liste_feuillet, creation):
    rep_metriques = None
    rep_mnt_buff = None
    for i in liste_feuillet:
        feuillet = i

        ftpdirectory = 'transfert.mffp.gouv.qc.ca'  # site ftp
        ftpparent = r'Public/Diffusion/DonneeGratuite/Foret/IMAGERIE/Produits_derives_LiDAR/'  # répertoire de base
        path_index = os.path.join(root_dir, 'inputs/MNT/index/Index_ProduitsDerive_LiDAR_Sweb.shp')
        col_feuillet = 'FCA_NO_FEU'  # colonne des numéro de feuillet dans la couche index
        rep_mnt = os.path.join(root_dir, 'inputs/MNT/originaux') # Répertoire contenant les MNT téléchargés

        # Intrants pour les prétraitements
        distance_buffer = 1000  # Distance pour le buffer autour du raster
        size_resamp = 5         # Taille de rééchantillonnage
        rep_mnt_buff = os.path.join(root_dir, 'inputs/MNT/resample') # Chemin des fichiers temporaires rééchantillonnés

        # Intrants pour la production de métriques
        rep_metriques = os.path.join(root_dir, 'inputs/tiffs', feuillet)  # Chemin vers le répertoire output des métriques
        mntbuff = os.path.join(rep_mnt_buff, feuillet[:-2], '{}_buffer.tif'.format(feuillet))
        path_script = os.path.join(root_dir, 'inputs/scripts/haralick.R') # Chemin vers le script 'haralick.R'

        if creation is True:
            # Appel des fonctions externes
            # Téléchargement des MNT si nécessaire
            mnts = download_mnt(feuillet=feuillet, path_index=path_index, col_feuillet=col_feuillet,
                                ftpparent=ftpparent, ftpdirectory=ftpdirectory, output=rep_mnt)
            # Prétraitements
            pretraitements(feuillet=feuillet, liste_path_feuillets=mnts, distance_buffer=distance_buffer,
                           size_resamp=size_resamp, rep_output=rep_mnt_buff)

            # Création des métriques
            creation_metriques(mnt=mntbuff, feuillet=feuillet, rep_output=rep_metriques, path_r=path_r, path_script=path_script)

    return rep_metriques, rep_mnt_buff


#### SECTION 2a - Échantillonage par pixel ####
'''
À REMPLIR
'''

def echant_main(liste_feuillet, creation):
    rep_metriques, rep_mnt_buff = mnt_metriques(liste_feuillet, creation) # Appel de variables de la SECTION 1
    for i in liste_feuillet:
        feuillet = i

        # Intrants pour l'échantillonnage par pixel
        path_depot = os.path.join(root_dir, 'inputs/depots', feuillet, 'zones_depots_glaciolacustres_{}.shp'.format(feuillet))  # Chemins des couches du MNT et de la couche de dépôts
        path_mnt = os.path.join(rep_mnt_buff, 'MNT_{}_resample.tif'.format(feuillet))
        echant = os.path.join(os.path.join(root_dir, 'inputs/ech_entrainement_mod/pixel', feuillet[:-2], 'ech_{}.shp'.format(feuillet)))

        # Échantillonnage par pixel
        echantillonnage_pix(path_depot=path_depot, path_mnt=path_mnt, path_metriques=rep_metriques,
                            output=echant, nbPoints=2000, minDistance=500)

#echant_main(liste_feuillet, creation=False)


#### SECTION 3a - (OPTIONNEL) Optimisation/recherche des hyperparamètres ####
'''
Recherche des paramètres optimaux pour l'entraînement du modèle
ATTENTION CE PROCESSUS PEUT ÊTRE TRÈS LONG !!!


À REMPLIR
'''

def gridSearch_params_opti(inputEch, metriques_pixel, outputMod):
    # Intrants pour l'optimisation des hyperparamètres du modele
    # Grille de paramètre pour le GridSearchCV
    param_grid = {
                  "n_estimators": [200, 500, 800, 1000, 5000, 10000],
                  "max_features": ['auto', 'sqrt', 'log2'],
                  "max_depth" : [None, 2, 4, 6, 8, 10]
                 }
    # Création du modèle de base
    params_base = {'n_estimators': 200}
    clf, accu_mod, train_metriques, train_y, test_metriques, test_y = entrainement(inputEch=inputEch, metriques=metriques_pixel,
                                                                                   outputMod=outputMod, **params_base)
    # Modele d'optimisation avec GridSearchCV
    modele_opti, params_opti = HyperTuningGrid(model_base=clf, param_grid=param_grid, x_train=train_metriques, y_train=train_y)
    print (params_opti) # Impression des meilleurs résultats basé sur param_grid

    return params_opti


# # Impression des courbes de validation pour chaque hyperparamètre
# for key, value in param_grid.items():  # Pour chaque items de la liste des paramètres à optimiser
#     plot_valid(param_name=key, param_range=value, modele=clf, x_train=train_metriques, y_train=train_y)



#### SECTION 4a - Entraînement du modèle par pixel  ####
'''
À REMPLIR
avec matrice de confusion et importance des métriques
'''

def entrain_main(feuillet, opti=False):
    # # Intrants pour l'entraînement du modele
    metriques_pixel = ['ANVAD', 'ConH', 'CorH', 'CVA', 'DI', 'ED', 'MeaH', 'PC', 'Pen', 'SSDN', 'TPI', 'TWI']
    #metriques_pixel = ['ANVAD', 'ConH', 'CorH', 'CVA', 'DI', 'ED', 'PC', 'Pen', 'SSDN', 'TPI', 'TWI']
    inputEch = os.path.join(os.path.join(root_dir, 'inputs/ech_entrainement_mod/pixel/', feuillet[:-2]))
    outputMod = os.path.join(os.path.join(root_dir, 'inputs/modeles', feuillet[-7:-2]))

    if opti is True:
        print('Début de GridSearchCV pour trouver les paramètres optimaux')
        params_opti = gridSearch_params_opti(inputEch=inputEch, metriques_pixel=metriques_pixel, outputMod=outputMod)
        print('Fin du GridSearchCV')
    else :
        # Utilise les paramètres optimisés issues de l'étape optimisation
        params_opti = {'max_depth': None, 'max_features': 'auto', 'n_estimators': 5000}

    print('Début de l\'entrainement du modèle')
    clf, accu_mod, train_metriques, train_y, test_metriques, test_y = entrainement(inputEch=inputEch, metriques=metriques_pixel,
                                                                                   outputMod=outputMod, **params_opti)
    print('Fin de l\'entrainement du modèle en utilisant les paramètres :')
    print(params_opti)

    return clf, accu_mod, params_opti, train_metriques, train_metriques, test_metriques, test_y

# for i in liste_feuillet:
#     echant_main(liste_feuillet, creation=False)
#
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
    mod_path = os.path.join(root_dir, 'inputs/modeles')              # Chemin vers le dossier des modèles
    rep_metriques = os.path.join(root_dir, 'inputs/tiffs', feuillet) # Chemin vers le dossier des métriques
    nom_fichier = 'prediction_{}.tif'.format(feuillet)               # Nom du fichier à sauvegarder
    outputdir = os.path.join(root_dir, 'outputs/pixel')              # Dossier output du .shp prédit

    # Classification avec le modèle et création du fichier résultant
    classif, tiff_path_list = classification(num_mod=num_mod, mod_path=mod_path, rep_metriques=rep_metriques)
    creation_output(prediction=classif, outputdir=outputdir, nom_fichier=nom_fichier,
                    inputMet=rep_metriques, tiff_path_list=tiff_path_list)

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

# # Commencer par déterminer les feuillets que l'on désire traiter
# liste_feuillet = ['32D01NO', '32D01SO']
#
# echant_main(liste_feuillet, creation=True)
#

# Entrainement du modèle
#entrain_main('32D01NO', opti=True)

# Classification d'un feuillet
#class_main(feuillet='31H02SE', num_mod='31H02')
# # Intrants pour l'entraînement du modele
feuillet = '31H02NE'
metriques_pixel = ['ANVAD', 'ConH', 'CorH', 'CVA', 'DI', 'ED', 'MeaH', 'PC', 'Pen', 'SSDN', 'TPI', 'TWI']
# metriques_pixel = ['ANVAD', 'ConH', 'CorH', 'CVA', 'DI', 'ED', 'PC', 'Pen', 'SSDN', 'TPI', 'TWI']
inputEch = os.path.join(os.path.join(root_dir, 'inputs/ech_entrainement_mod/pixel/', feuillet[:-2]))
outputMod = os.path.join(os.path.join(root_dir, 'inputs/modeles', feuillet[-7:-2]))

param_grid = {
              "n_estimators": [200, 500, 800, 1000, 5000, 10000],
              "max_features": ['auto', 'sqrt', 'log2'],
              "max_depth" : [None, 2, 4, 6, 8, 10]
             }
# Création du modèle de base
params_base = {'n_estimators': 200}
clf, accu_mod, train_metriques, train_y, test_metriques, test_y = entrainement(inputEch=inputEch, metriques=metriques_pixel,
                                                                                   outputMod=outputMod, **params_base)

# # Impression des courbes de validation pour chaque hyperparamètre
param_range = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

#param_range.append()
#param_range.append(None)
#param_range = [200, 500, 800, 1000, 5000, 10000]
#param_range = ['auto', 'sqrt', 'log2']
plot_valid(param_name='max_depth', param_range=param_range, modele=clf, x_train=train_metriques, y_train=train_y)



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