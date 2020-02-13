'''
INTRANTS:

- path => path de la métrique
- path_couche_depots => path de la couche .shp des zones de dépôts pour le même feuillet que celui la métrique, dans la
  même projection
- temp => path du répertoire temporaire

'''

from fonctions_echantillonnage import *
import os
import pandas as pd
import shutil

path_metrique = r'D:\DATA\TPI_WB\31H02\RelTPI_WB_31H02SE.tif'
path_couche_depots = r'D:\DATA\shapefile\Depots_31H\zone_depots_glaciolacustre_31H02SE_MTM8.shp'
path_sauvegarde_csv = r'D:\DATA\Echantillons_metrique2'
path_sauvegarde_figures = r'D:\DATA\Figures'
temp = r'D:\DATA\temp'


# Création des rasters de masques de zones de dépôts à partir des polygones

print('Création des masques...')
masques = creation_masque(path_couche_depots, path_metrique, temp)
print('Terminé')
print()

# échantillonnage

print('Échantillonnage...')
vals = echantillonnage(masques[0], masques[1], temp, path_metrique)
print('Terminé')
print()

# Représentation graphique

print('Création des histogrammes de fréquence...')

dic_metrique = {'RelTPI': 'TPI', 'TWI':'TWI', 'Pente': 'Pente', 'CirVarAspect':'Circular variance of aspect'}
pseudo = os.path.split(path_metrique)[-1].split('_')[0]
metrique = dic_metrique[pseudo]
feuillet = os.path.split(path_metrique)[-1].split('_')[2].split('.')[0]

histogramme(vals, 'in_zone', metrique=metrique, feuillet=feuillet, output=path_sauvegarde_figures)
histogramme(vals, 'out_zone', metrique=metrique, feuillet=feuillet, output=path_sauvegarde_figures)
print('Terminé')
print()

# sauvegarde des échantillons en format CSV

print('Enregistrement des échantillons en format csv...')
data = pd.DataFrame(vals)
nom = os.path.split(path_metrique)[-1].replace('.tif', '.csv')
path_csv = os.path.join(path_sauvegarde_csv, nom)
data.to_csv(path_csv, index=False)
print('Terminé')
print()

# Suppression des fichiers du répertoire temporaire

path_shp_echan = os.path.join(os.path.dirname(temp), 'Shapefile_echantillons')
if not os.path.exists(path_shp_echan):
    os.makedirs(path_shp_echan)
print('Copie des fichiers de points avec les valeurs dans {} et suppression des fichiers temporaires'.format(path_shp_echan))
for file in os.listdir(temp):
    if 'random_values' in file and (file.endswith('.prj') or file.endswith('.shp') or file.endswith('dbf') or file.endswith('.shx')):
        extension = file[-4:]
        in_out = file.split('.')[0].split('_')[-1]
        new_file = os.path.join(path_shp_echan, '{}_{}_{}{}'.format(pseudo, feuillet,in_out, extension))
        os.rename(os.path.join(temp,file), new_file)
        #shutil.move(os.path.join(temp, new_file), path_shp_echan)
    else:
        os.remove(os.path.join(temp, file))
print('Terminé')
print()

