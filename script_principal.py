from Download_MNT import download_mnt
from pretraitements import pretraitements
from production_metriques import creation_metriques
from ech_pixel import echantillonnage_pix
import os

feuillet = '32D06NE'

root_dir = os.path.abspath(os.path.dirname(__file__))


# Intrants pour le téléchargement
ftpdirectory = 'transfert.mffp.gouv.qc.ca'  # site ftp
ftpparent = r'Public/Diffusion/DonneeGratuite/Foret/IMAGERIE/Produits_derives_LiDAR/'  # répertoire de base
path_index = r'C:\Users\home\Documents\Documents\APP3\Index_produit_derive_lidar\Index_produit_derive_lidar\Index_ProduitsDerive_LiDAR_Sweb.shp'
col_feuillet = 'FCA_NO_FEU'  # colonne des numéro de feuillet dans la couche index
rep_mnt = r'C:\Users\home\Documents\Documents\APP2\mnt'  # Répertoire contenant les MNT téléchargés

# Intrants pour les prétraitements
distance_buffer = 1000  # Distance pour le buffer autour du raster
size_resamp = 5  # Taille de rééchantillonnage
rep_mnt_buff = r'C:\Users\home\Documents\Documents\APP3\mnt_buffer'


# Intrants pour la production de métriques
rep_metriques = os.path.join(root_dir, 'inputs/tiffs', feuillet)  # Chemin vers le répertoire output des métriques
# rep_metriques = r'C:\Users\home\Documents\Documents\APP3\metriques'
path_r = r"C:\Program Files\R\R-3.6.3\bin\Rscript.exe"  # Chemin vers l'application 'Rscript.exe'
path_script = r"C:\Users\home\Documents\Documents\APP2\haralick.R"  # Chemin vers le script 'haralick.R'

# Intrants pour l'échantillonnage par pixel
path_depot = r'C:\Users\home\Documents\Documents\APP2\depots_31H02\zones_depots_glaciolacustres_31H02SE_MTM8.shp'  ## Chemins des couches du MNT et de la couche de dépôts
path_mnt = r'C:\Users\home\Documents\Documents\APP2\MNT_31H02SE_5x5.tif'
path_metriques = r'C:\Users\home\Documents\Documents\APP2\Metriques\31H02\31H02SE'
echant = os.path.join(os.path.join(root_dir, 'inputs/inputs_modele_avril2020', 'ech_{}.shp'.format(feuillet)))


# Téléchargement des MNT si nécessaire
mnts = download_mnt(feuillet=feuillet, path_index=path_index, col_feuillet=col_feuillet,
                    ftpparent=ftpparent, ftpdirectory=ftpdirectory, output=rep_mnt)

# Prétraitements
pretraitements(feuillet=feuillet, liste_path_feuillets=mnts, distance_buffer=distance_buffer,
               size_resamp=size_resamp, rep_output=rep_mnt_buff)

# Création des métriques
creation_metriques(rep_mnt=rep_mnt_buff, rep_output=rep_metriques, path_r=path_r, path_script=path_script)


# Échantillonnage par pixel
echantillonnage_pix(path_depot=path_depot, path_mnt=path_mnt, path_metriques=path_metriques,
                    output=echant, nbPoints=2000, minDistance=500)
