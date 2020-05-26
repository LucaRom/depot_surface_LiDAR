from Download_MNT import download_mnt
from pretraitements import pretraitements
from production_metriques import creation_metriques
from ech_pixel import echantillonnage_pix
import os


feuillet = '31H02NE'
root_dir = os.path.abspath(os.path.dirname(__file__))

# Intrants pour le téléchargement
ftpdirectory = 'transfert.mffp.gouv.qc.ca'  # site ftp
ftpparent = r'Public/Diffusion/DonneeGratuite/Foret/IMAGERIE/Produits_derives_LiDAR/'  # répertoire de base
path_index = os.path.join(root_dir, 'inputs/MNT/index/Index_ProduitsDerive_LiDAR_Sweb.shp')
col_feuillet = 'FCA_NO_FEU'  # colonne des numéro de feuillet dans la couche index
#rep_mnt = r'C:\Users\home\Documents\Documents\APP2\mnt'  # Répertoire contenant les MNT téléchargés
rep_mnt = os.path.join(root_dir, 'inputs/MNT/originaux')

# Intrants pour les prétraitements
distance_buffer = 1000  # Distance pour le buffer autour du raster
size_resamp = 5  # Taille de rééchantillonnage
#rep_mnt_buff = r'C:\Users\home\Documents\Documents\APP3\mnt_buffer'
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

# Téléchargement des MNT si nécessaire
mnts = download_mnt(feuillet=feuillet, path_index=path_index, col_feuillet=col_feuillet,
                    ftpparent=ftpparent, ftpdirectory=ftpdirectory, output=rep_mnt)

# Prétraitements
pretraitements(feuillet=feuillet, liste_path_feuillets=mnts, distance_buffer=distance_buffer,
               size_resamp=size_resamp, rep_output=rep_mnt_buff)

# Création des métriques
creation_metriques(mnt=mntbuff, feuillet=feuillet, rep_output=rep_metriques, path_r=path_r, path_script=path_script)


# Échantillonnage par pixel
echantillonnage_pix(path_depot=path_depot, path_mnt=path_mnt, path_metriques=rep_metriques,
                    output=echant, nbPoints=4000, minDistance=500)

# Suppression des fichiers
for files in os.listdir(rep_mnt_buff):
    path = os.path.join(rep_mnt_buff, files)
    if os.path.isdir(path) is False:
        os.remove(path)

