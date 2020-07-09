# -*- coding: utf-8 -*-

"""
Created on Wed Jan 2020
@authors: David Ethier  david.ethier2@usherbrooke.ca
          Luca Romanini luca.romanini@usherbrooke.ca

"""

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

# Paramètres initiaux du script
root_dir = os.path.abspath(os.path.dirname(__file__))   # Définition du chemin racine du dossier de travail
path_r = r"E:\Program Files\R\R-3.6.1\bin\Rscript.exe"  # Chemin vers l'application 'Rscript.exe' de l'ordinateur


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
           sur l'ordinateur que vous utilisez. Voir la variable "path_r" au début de ce présent script.
       
'''

def mnt_metriques(liste_feuillet, creation):
    """
    :param liste_feuillet: Spécifier une liste (ex. liste = [31H02SE, 31H02NE]) pour créer les métriques sur un
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


#### SECTION 2 - Échantillonage pixel et objet ####
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

#### SECTION 3 - (OPTIONNEL) Optimisation/recherche des hyperparamètres ####
'''
Cette section contient la fonction qui recherche les paramètres optimaux pour l'entraînement du modèle

Dans l'ordre, le code : 1) Définie une liste de valeurs à tester par paramètres spécifié par l'utilisateur
                        2) Crée un modèle de base défini par l'utilisateur
                        3) Teste chaque combinaison possible des paramètres

Résultats : La variable retourné "params_opti" contient les paramètres optimaux du modèle testé selon les valeurs 
            utilisées. Peut être utilisé comme paramètre des fonctions d'entraînement (entrain_main_pix, entrain_main_obj).
                        
NOTES : #### ATTENTION CE PROCESSUS PEUT ÊTRE TRÈS LONG !!! ####
'''

def gridSearch_params_opti(zone_feuillets, approche):
    """
    :param zone_feuillets: Spécifier la zone d'entraînement contenant tous les fichiers échantillonée (Ex.: 31H02)
    :param approche: Spécifier s'il s'agit de l'approche pixel ou objet
    """
    # Paramètres communs aux deux approches
    outputMod = os.path.join(root_dir, 'inputs/modeles', zone_feuillets)  # Chemin de sortie pour la sauvegarde du modèle

    if approche == 'pixel':
        # Intrants pour l'échantillonnage par pixel
        inputEch = os.path.join(root_dir, 'inputs/ech_entrainement_mod/pixel/', zone_feuillets) # Chemin vers les fichiers d'échantillonage du feuillet
        liste_metriques = ['ANVAD', 'ConH', 'CorH', 'CVA', 'DI', 'ED', 'MeaH', 'PC', 'Pen', 'SSDN', 'TPI', 'TWI'] # Liste des métriques utilisés pour l'entraînement

    elif approche == 'objet':
        # Intrants pour l'échantillonnage par pixel
        inputEch = os.path.join(root_dir, 'inputs/ech_entrainement_mod/pixel/', zone_feuillets)
        liste_metriques = ['ANVAD_min', 'ANVAD_max', 'ANVAD_medi', 'ANVAD_mean', 'ANVAD_std', 'ConH_min', 'ConH_max',
                           'ConH_media', 'ConH_mean', 'ConH_std', 'CorH_min', 'CorH_max', 'CVA_min', 'CVA_max',
                           'CVA_median', 'CVA_mean', 'CVA_std', 'DI_min', 'DI_max', 'DI_median', 'DI_mean', 'DI_std',
                           'ED_min', 'ED_max', 'ED_median', 'ED_mean', 'ED_std', 'MeaH_min', 'MeaH_max', 'MeaH_media',
                           'MeaH_mean', 'MeaH_std', 'PC_min', 'PC_max', 'PC_median', 'PC_mean', 'PC_std', 'Pen_min',
                           'Pen_max', 'Pen_median', 'Pen_mean', 'Pen_std', 'SSDN_min', 'SSDN_max', 'SSDN_media',
                           'SSDN_mean', 'SSDN_std', 'TPI_min', 'TPI_max', 'TPI_median', 'TPI_mean', 'TPI_std',
                           'TWI_min', 'TWI_max', 'TWI_median', 'TWI_mean', 'TWI_std']

    # Grille de paramètres pour le GridSearchCV
    param_grid = {
        "n_estimators": [200, 500, 800, 1000, 5000, 10000],
        "max_features": ['auto', 'sqrt', 'log2'],
        "max_depth": [None, 2, 4, 6, 8, 10]
    }

    # Création du modèle de base
    params_base = {'n_estimators': 200}
    clf, accu_mod, train_metriques, train_y, test_metriques, test_y = entrainement_pix(inputEch=inputEch,
                                                                                       metriques=liste_metriques,
                                                                                       outputMod=outputMod,
                                                                                       replaceMod=False,
                                                                                       makeplots=False, **params_base)

    # Optimisation avec GridSearchCV (sickit-learn)
    modele_opti, params_opti = HyperTuningGrid(model_base=clf, param_grid=param_grid, x_train=train_metriques,
                                               y_train=train_y)

    #print(params_opti)  # Impression des meilleurs résultats basé sur param_grid

    return params_opti


#### SECTION 4a - Entraînement du modèle par pixel  ####
'''
Cette section entraîne un modèle de type Random Forest en utilisant les données des métriques échantillonnées pour 
l'approche par pixel.

Dans l'ordre, le code : 1) Vérifie quels paramètres optimaux utilisés ou, le cas échéant s'il doit faire l'étape 
                           d'optimisation
                        2) Crée les figures de matrices de confusion et d'importance des métriques
                        3) Entraîne le modèle
                        
Résultats : - À l'issue de cette étape, un modèle en format .pkl est sauvegardé dans ./inputs/modeles/ pour être utilisé 
              à l'étape de la classification.
            - Cette étape produit aussi deux figures : 1) Matrice de confusion 2) Importance des métriques

NOTES : 1) Il est important de lire les détails des paramètres de la fonction au début de cette dernière
           
        2) Les métriques utilisés pour le modèle sont inclues dans la fonction et doivent être modifiée manuellement si 
           besoin. 
       
'''


def entrain_main_pix(zone_feuillets, opti=False, makeplots=False, replaceMod=False):
    """
    :param zone_feuillets: Spécifier la zone d'entraînement contenant tous les fichiers échantillonée (Ex.: 31H02)
    :param opti: Spécifier le modèle pour lequel les paramètres ont déjà été optimisé (ex.: '31H02'). Si on met la valeur
                 True, l'algorithme va lancer le processus de recherches de paramètres optimaux et utiliser les résultats
                 pour entraîner le modèle. ATTENTION, ceci peut-être très long.
    :param makeplots: Booléen (True/False). Si True, les figures sont produites.
    :param replaceMod: Booléen (True/False). Si True, le un modèle sera sauvegardé pour cette région. Si un modèle existe
                       déjà, il sera écrasé.
    """
    # # Intrants pour l'entraînement du modele
    metriques_pixel = ['ANVAD', 'ConH', 'CorH', 'CVA', 'DI', 'ED', 'MeaH', 'PC', 'Pen', 'SSDN', 'TPI', 'TWI'] # Liste des métriques utilisés pour l'entraînement
    inputEch = os.path.join(root_dir, 'inputs/ech_entrainement_mod/pixel/', zone_feuillets) # Chemin vers les fichiers d'échantillonage de la zone
    outputMod = os.path.join(root_dir, 'inputs/modeles', zone_feuillets) # Chemin de sortie pour la sauvegarde du modèle

    if opti is True: # Lance le processus d'optimisation
        # Utilise les paramètres optimisés issues de l'étape optimisation
        print('Début de GridSearchCV pour trouver les paramètres optimaux')
        params_opti = gridSearch_params_opti(zone_feuillets=feuillet[:-2], approche='pixel')
        print('Fin du GridSearchCV')
    elif opti == '31H02': # Utilise les paramètres optimaux pour le modèle 31H02 (Fait auparavant)
        print('Début de l\'entrainement avec les paramètres optimisé pour la zone 31H02')
        # params_opti = {'max_depth': 4, 'max_features': 'auto', 'n_estimators': 1000}
        params_opti = {'max_depth': 7, 'max_features': 'auto', 'n_estimators': 1000}
    elif opti == '32D01':  # Utilise les paramètres optimaux pour le modèle 32D01 (Fait auparavant)
        print('Début de l\'entrainement avec les paramètres optimisé pour la zone 32D01')
        params_opti = {'max_depth': 4, 'max_features': 'auto', 'n_estimators': 5000}
    else: # Lance un entraînement avec des paramètres de base, non optimisé.
        params_opti = {'max_depth': None, 'max_features': 'auto', 'n_estimators': 1000}

    # Appel de la fonction d'entraînement pour l'approche par pixel (fonctions_modele.py)
    print('Début de l\'entrainement du modèle')
    clf, accu_mod, train_metriques, train_y, test_metriques, test_y = entrainement_pix(inputEch=inputEch,
                                                                                       metriques=metriques_pixel,
                                                                                       outputMod=outputMod,
                                                                                       replaceMod=replaceMod,
                                                                                       makeplots=makeplots,
                                                                                       **params_opti)
    print('Fin de l\'entrainement du modèle en utilisant les paramètres :')

    return clf, accu_mod, params_opti, train_metriques, train_metriques, test_metriques, test_y


#### SECTION 4b - Entraînement du modèle par objet  ####
'''
Cette section est construite de la même façon que l'approche par pixel (Section 4a). Les différences proviennent des 
fichiers sources d'entraînements qui sont différents (segmentation). Les paramètres optimisés pour chacun des zones
sont aussi différents.
'''

def entrain_main_obj(zone_feuillets, opti=False, makeplots=False, replaceMod=False):
    # # Intrants pour l'entraînement du modele
    inputEch = os.path.join(os.path.join(root_dir, 'inputs/ech_entrainement_mod/objet/', zone_feuillets))
    outputMod = os.path.join(os.path.join(root_dir, 'inputs/modeles', zone_feuillets))

    #print(inputEch)

    if opti is True:
        print('Début de GridSearchCV pour trouver les paramètres optimaux')
        params_opti = gridSearch_params_opti(zone_feuillets=zone_feuillets, approche='objet')
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

    return clf, accu_mod, params_opti, train_metriques, train_metriques, test_metriques, test_y


#### SECTION 5a - Classification par pixel ####
'''
Cette section utilise un modèle entraîné pour faire la prédiction de classe sur un feuillet pour l'approche par pixel.

Dans l'ordre, le code : 1) Importe le modèle désiré
                        2) Classifie le feuillet

Résultats : - Un fichier .tiff est obtenu dans ./fichiers_outputs/pixel/

NOTES : 1) Pour faire la prédiction d'un feuillet, il faut lancer la fonction "mnt_metriques" (Section 1) auparavant
        2) IMPORTANT : En tout temps, les métriques du feuillet doivent être les mêmes que lors de l'entraînement du 
           modèle sélectionné pour la prédiction.
       
'''

def class_main(feuillet, num_mod):
    """
    :param feuillet: Numéro du feuillet à classer (ex. '31H02SO')
    :param num_mod: Numéro du modèle déjà entraîné provenant du dossier ./inputs/modeles/
    """
    # # Intrants pour la classification du modèle
    mod_path = os.path.join(root_dir, 'inputs/modeles')               # Chemin vers le dossier des modèles
    rep_metriques = os.path.join(root_dir, 'inputs/tiffs', feuillet)  # Chemin vers le dossier des métriques
    nom_fichier = 'prediction_{}_{}.tif'.format(feuillet, num_mod)    # Nom du fichier à sauvegarder
    outputdir = os.path.join(root_dir, 'fichiers_outputs/pixel')      # Dossier output du .tif prédit

    # Classification avec le modèle
    classif, tiff_path_list = classification(num_mod=num_mod, mod_path=mod_path,    # Appel de la fonction de classification
                                             rep_metriques=rep_metriques)           # (fonctions_modele.py)

    # Création du fichier sortant '.tif'
    creation_output(prediction=classif, outputdir=outputdir, nom_fichier=nom_fichier,  # Appel de la fonction de création de fichier
                    inputMet=rep_metriques, tiff_path_list=tiff_path_list)             # (fonctions_modele.py)


#### SECTION 5b - Classification par objet####
'''
Cette section utilise un modèle entraîné pour faire la prédiction de classe sur un feuillet pour l'approche par objet.

Dans l'ordre, le code : 1) Importe la segmentation du feuillet
                        2) Importe le modèle désiré
                        2) Classifie le feuillet

Résultats : - Un fichier .sho est obtenu dans ./fichiers_outputs/objet/

NOTES : 1) Pour faire la prédiction d'un feuillet, il faut lancer la fonction "mnt_metriques" (Section 1) ainsi que 
            la fonction echant_main avec l'approche par objet (section 2) auparavant.
        2) IMPORTANT : En tout temps, les métriques spécifiées dans la fonction "met_seg" doivent être les mêmes que 
           lors de l'entraînement du modèle sélectionné pour la prédiction.
        3) Cette approche nécessite que la variable met_seg soit définie manuellement selon la sélection des métriques, 
           mais est automatisé si la combinaison de métrique est constante. 

'''
def class_main_obj(seg_num, mod_num):
    """
    :param seg_num: Numéro de la segmentation avec statistiques correspondante au feuillet que l'on veut prédire
    :param mod_num: Numéro du modèle entraîné avec lequel on désir effectuer la prédiction
    """

    # Définition des métriques utilisées lors de l'entraînement
    met_seg = ['ANVAD_min', 'ANVAD_max', 'ANVAD_medi', 'ANVAD_mean',
           'ANVAD_std', 'ConH_min', 'ConH_max', 'ConH_media', 'ConH_mean',
           'ConH_std', 'CorH_min', 'CorH_max', 'CVA_min', 'CVA_max', 'CVA_median',
           'CVA_mean', 'CVA_std', 'DI_min', 'DI_max', 'DI_median', 'DI_mean',
           'DI_std', 'ED_min', 'ED_max', 'ED_median', 'ED_mean', 'ED_std',
           'MeaH_min', 'MeaH_max', 'MeaH_media', 'MeaH_mean', 'MeaH_std', 'PC_min',
           'PC_max', 'PC_median', 'PC_mean', 'PC_std', 'Pen_min', 'Pen_max',
           'Pen_median', 'Pen_mean', 'Pen_std', 'SSDN_min', 'SSDN_max',
           'SSDN_media', 'SSDN_mean', 'SSDN_std', 'TPI_min', 'TPI_max',
           'TPI_median', 'TPI_mean', 'TPI_std', 'TWI_min', 'TWI_max', 'TWI_median',
           'TWI_mean', 'TWI_std']

    # Définition des chemins nécessaires à la fonction
    seg_path = os.path.join(root_dir, 'inputs/segmentations')         # Chemin vers le dossier des segmentations
    mod_path = os.path.join(root_dir, 'inputs/modeles')               # Chemin vers les modèles sauvegardés
    output_path =  os.path.join(root_dir, 'fichiers_outputs/objet')   # Chemin pour enregistrer le shapefile optenu

    # Lancement de la fonction de classification (fonctions_modele.py)
    classification_obj(seg_num=seg_num, seg_path=seg_path,
                       mod_path=mod_path, mod_num=mod_num,
                       met_seg=met_seg, output_path=output_path)


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

#### EXEMPLE D'UTILISATION DES FONCTIONS DANS UN "WORKFLOW" COMPLET

#### EX - SECTION 1 - Production des métriques ####

# Commencer par déterminer les feuillets que l'on désire traiter
liste_feuillet = ['32D02SE'] # Ici on spécifie qu'un seul feuillet, mais plusieurs pourraient être spécifié

#Appel de la fonction et spécification des paramètres
mnt_metriques(liste_feuillet=liste_feuillet, creation=True) # Ici on spécifie qu'on veut crée ou remplacer les fichiers
                                                            # de métrique(creation=True).

#### EX - SECTION 2 - Échantillonage pixel et objet #### (À COMPLÉTER)

echant_main(liste_feuillet, creation=True, approche='pixel') # Ici on spécifie qu'on veut crée ou remplacer les fichiers
                                                             # d'échantillonage (creation=True) et qu'on est dans une
                                                             # approche par pixel.
                                                             # La liste des feuillets peut être spécifié si on utilise
                                                             # la fonction de façon autonome.

#### EX - SECTION 3 - (OPTIONNEL) Optimisation/recherche des hyperparamètres ####
# Cette fonction peut-être utilisé seule, mais sera plus souvent utilisé à l'intérieur de la fonction d'entraînement
# afin de spécifier les paramètres optimaux de façon automatique.

gridSearch_params_opti(zone_feuillets='31H02', approche='pixel') # Ici on spécifie qu'on veut entraîner le modèle avec
                                                                 # les échantillons de la zone '31H02' et qu'on utilise
                                                                 # l'approche par pixel.

#### SECTION 4a - Entraînement du modèle par pixel  ####
# Entrainement du modèle par pixel

entrain_main_pix('31H02', opti='31H02', makeplots=True, replaceMod=True) # Ici on spécifie qu'on veut entraîner le modèle avec
                                                                         # les échantillons de la zone '31H02' et qu'on utilise
                                                                         # les paramètres optimisés obtenus précédemment pour
                                                                         # cette même région (opti='31H02').
                                                                         # On demande de crée les figures (makeplots=True)
                                                                         # On demande d'enregistrer/remplacer le modèle (replaceMod=True)

#### SECTION 4b - Entraînement du modèle par objet  ####
# Entrainement du modèle par pixel

entrain_main_obj('31H02', opti='31H02', makeplots=True, replaceMod=True) # Voir commentaires 4a


#### SECTION 5a - Classification par pixel ####
# Classification d'un feuillet
class_main(feuillet='31H02SO', num_mod='31H02') # Ici on classifie le feuillet 31H02SO avec le modèle entraîné nommé
                                                # 31H02. (Les métriques ont été faites auparavant pour le feuillet 31H02SO)


#### SECTION 5a - Classification par pixel ####
# Classification d'un feuillet
class_main_obj(seg_num='seg_stats_31H02SE_v2', num_mod='31H02_obj_seg') # Ici on classifie le feuillet segmenté 31H02SE
                                                                        # avec le modèle par objet de la zone 31H02.
                                                                        # La segmentation et le calculs des faits
                                                                        #  auparavant pour le feuillet 31H02SO)


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
