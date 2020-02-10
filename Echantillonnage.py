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

path_metrique = r'D:\DATA\TPI_WB\31H02\RelTPI_WB_31H02SE.tif'
path_couche_depots = r'D:\DATA\shapefile\Depots_31H\zone_depots_glaciolacustre_31H02SE_MTM8.shp'
path_sauvegarde_csv = r'D:\DATA\echantillons_metriques'
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

print('Suppression des fichiers temporaires...')
for file in os.listdir(temp):
    os.remove(os.path.join(temp, file))
print('Terminé')
print()

