from Download_MNT import download_mnt
from pretraitements import pretraitements
from production_metriques import creation_metriques
from ech_pixel import echantillonnage_pix
from fonctions_modele import entrainement, classification, creation_output
import os
from osgeo import gdal

feuillet = '31H02SE'
root_dir = os.path.abspath(os.path.dirname(__file__))

# Intrants pour le téléchargement
ftpdirectory = 'transfert.mffp.gouv.qc.ca'  # site ftp
ftpparent = r'Public/Diffusion/DonneeGratuite/Foret/IMAGERIE/Produits_derives_LiDAR/'  # répertoire de base
path_index = os.path.join(root_dir, 'inputs/MNT/index/Index_ProduitsDerive_LiDAR_Sweb.shp')
col_feuillet = 'FCA_NO_FEU'  # colonne des numéro de feuillet dans la couche index
rep_mnt = os.path.join(root_dir, 'inputs/MNT/originaux') # Répertoire contenant les MNT téléchargés

# Intrants pour les prétraitements
distance_buffer = 1000  # Distance pour le buffer autour du raster
size_resamp = 5  # Taille de rééchantillonnage
rep_mnt_buff = os.path.join(root_dir, 'inputs/MNT/resample')

# Intrants pour la production de métriques
rep_metriques = os.path.join(root_dir, 'inputs/tiffs', feuillet)  # Chemin vers le répertoire output des métriques
mntbuff = os.path.join(rep_mnt_buff, feuillet[:-2], '{}_buffer.tif'.format(feuillet))
path_r = r"E:\Program Files\R\R-3.6.1\bin\Rscript.exe"  # Chemin vers l'application 'Rscript.exe'
path_script = os.path.join(root_dir, 'inputs/scripts/haralick.R') # Chemin vers le script 'haralick.R'

# Intrants pour l'échantillonnage par pixel
path_depot = os.path.join(root_dir, 'inputs/depots', feuillet, 'zones_depots_glaciolacustres_{}_MTM8.shp'.format(feuillet))  # Chemins des couches du MNT et de la couche de dépôts
path_mnt = os.path.join(rep_mnt_buff, 'MNT_{}_resample.tif'.format(feuillet))
echant = os.path.join(os.path.join(root_dir, 'inputs/ech_entrainement_mod/pixel', 'ech_{}.shp'.format(feuillet)))

# Intrants pour l'entraînement du model
metriques_pixel = ['ANVAD', 'ConH', 'CorH', 'CVA', 'DI', 'ED', 'MeaH', 'PC', 'Pen', 'SSDN', 'TPI', 'TWI']
inputEch = os.path.join(os.path.join(root_dir, 'inputs/ech_entrainement_mod/pixel'))

# Intrants pour la classification du modèle
tiff_path_list = os.listdir(rep_metriques)  # Liste des fichiers
# On crée une liste avec toutes les images lues
tiffs_list = []
for i in tiff_path_list:
    if i.endswith('.tif'):
        ds = gdal.Open(os.path.join(rep_metriques, i))
        tiffs_list.append(ds.GetRasterBand(1).ReadAsArray())

# Intrants pour la creation des outputs de prédiction (inclut dans la section "classification de modèle"
outputdir = os.path.join(root_dir, 'outputs/pixel') # Dossier
nom_fichier = 'prediction_{}.tif'.format(feuillet)


# #### FIN DES INTRANTS ####
#
# #### DÉBUT DES TRAITEMENTS ####
#
# # Téléchargement des MNT si nécessaire
# mnts = download_mnt(feuillet=feuillet, path_index=path_index, col_feuillet=col_feuillet,
#                     ftpparent=ftpparent, ftpdirectory=ftpdirectory, output=rep_mnt)
#
# # Prétraitements
# pretraitements(feuillet=feuillet, liste_path_feuillets=mnts, distance_buffer=distance_buffer,
#                size_resamp=size_resamp, rep_output=rep_mnt_buff)
#
# # Création des métriques
# creation_metriques(mnt=mntbuff, feuillet=feuillet, rep_output=rep_metriques, path_r=path_r, path_script=path_script)
#
#
# # Échantillonnage par pixel
# echantillonnage_pix(path_depot=path_depot, path_mnt=path_mnt, path_metriques=rep_metriques,
#                     output=echant, nbPoints=4000, minDistance=500)
#
# Entrainement du modèle et matrice de confusion/importance des métriques
clf, plt = entrainement(inputEch=inputEch, metriques=metriques_pixel)

# Classification avec le modèle et création du fichier résultant
classif = classification(clf=clf, tiffs_list=tiffs_list)
creation_output(prediction=classif, outputdir=outputdir, nom_fichier=nom_fichier,
                inputMet=rep_metriques, tiff_path_list=tiff_path_list)

# Suppression des fichiers
for files in os.listdir(rep_mnt_buff):
    path = os.path.join(rep_mnt_buff, files)
    if os.path.isdir(path) is False:
        os.remove(path)

# # À mettre à la fin d'entrainement modèle
#print('Fin de l\'entrainement, veuillez fermer les graphiques pour continuer')
print('Fin du script, veuillez fermer les graphiques pour terminer')
plt.show() # Garder les graphiques ouverts jusqu'à la fin si nécessaire