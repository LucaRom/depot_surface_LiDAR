# -*- coding: utf-8 -*-

"""
Created on Wed Jan 2020
@author: Luca Romanini

"""

# Import des librairies
import geopandas as gpd
from tifffile import imread
import matplotlib.pyplot as plt
import numpy as np
import os
from osgeo import gdal
from gdalconst import *
import pandas as pd

from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics

#### PARAMETRE INITIAUX ####
# On définit le dossier parent pour le réutiliser dans l'import d'intrants
root_dir  = os.path.dirname("__file__")

# On ajoute la date au fichier sortant pour suivre nos tests
date_classi = str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))

#### PARAMETRES A CHANGER ####
# Chemin des images pour faire à classer
tiffs_path = os.path.join(root_dir, 'inputs/tiffs/31H02NE_50m/') # Définition du chemin pour les images

# Chemin vers le dossier Output
out_tiffs = 'outputs/pixel_50m'

# Structure du nom du fichier sortant
nom_fichier = '31H02NE_50m_8mets' + date_classi + '.tiff'

# Liste des paramètres à conserver et à enlever(POUR RÉFÉRENCE)
# Liste complète
# ANVAD (0), CVA (1), ContHar (2), CorHar (3), DI (4), ED (5), MeanHar (6), Pente (7), ProfCur (8), TPI (9), SSDN (10), TWI (11)

# Conserver (8)
# ANVAD, CVA, ContHar, DI, MeanHar, Pente, TPI, SSDN

# Enlever (4)
# CorHar (2), ED (5), ProfCur (8), TWI (11)

#### Entraînement du modèle de classification ####

# Pour importer un shapefile
# Chemin vers le dossier avec les shapefiles
folder_path = os.path.join(root_dir, 'inputs/inputs_modele_avril2020') #### NE CHANGE PAS

# # On crée la liste des shapefiles
files = os.listdir(folder_path)  # Liste des fichiers dans le dossier "folder"
shp_list = [os.path.join(folder_path, i) for i in files if i.endswith('.shp')] # Obtenir une liste des chemins pour
                                                                                # .shp seulement
# On join les fichiers .shp de la liste
new_shp = gpd.GeoDataFrame(pd.concat([gpd.read_file(i) for i in shp_list],
                                      ignore_index = True), crs = gpd.read_file(shp_list[0]).crs)

# On choisi la colonne de que l'on veut prédire (ici le type de dépots)
y_depots = new_shp.Zone

# On definit les métriques sur lesquels on veut faire l'analyse
metriques = ['ANVAD', 'CVA', 'ContHar', 'CorHar', 'DI', 'EdgeDens', 'MeanHar', 'Pente', 'ProfCur', 'TPI', 'SSDN', 'TWI']
X_metriques = new_shp[metriques]

# Séparation des données en données d'entrainement et données de tests
train_metriques, test_metriques, train_y, test_y = train_test_split(X_metriques, y_depots, test_size = 0.30, random_state = 42)

# Create a Gaussian Classifier
clf = RandomForestClassifier(n_estimators = 500, verbose = 2, oob_score = True, random_state = 42)

# Train the model using the training sets y_pred=clf.predict(X_test)
clf.fit(train_metriques, train_y)

y_pred = clf.predict(test_metriques)

# Impression de précision
print("Accuracy:", metrics.accuracy_score(test_y, y_pred))

# Pour impression graphique
importances = clf.feature_importances_
indices = np.argsort(importances)

# plot them with a horizontal bar chart
plt.figure() # Crée une nouvelle instance de graphique
plt.title('Importances des métriques')
plt.barh(range(len(indices)), importances[indices], color='b', align='center')
plt.yticks(range(len(indices)), [metriques[i] for i in indices])
plt.xlabel('Importance relative (%)')
plt.show()

#### Prediction des pixels avec les matrices de métriques ####

# import os
# from tifffile import imread
# import numpy as np
#
# from osgeo import gdal
# from gdalconst import *

# Temporairement transposé en haut de page (ou permanent?)

# On importe le modèle de classification fait auparavant
''' À Compléter'''

metriques = ['ANVAD', 'CVA', 'ContHar', 'CorHar', 'DI', 'EdgeDens', 'MeanHar', 'Pente', 'ProfCur', 'TPI', 'SSDN', 'TWI']
# Import des images en matrices numpy
tiff_path_list = os.listdir(tiffs_path)

# On crée une liste avec toutes les images lues
tiffs_list = []
for i in tiff_path_list:
    tiffs_list.append(imread(os.path.join(tiffs_path, i)))

# On crée la liste des metrics pour les itérer
#image_list = [met1, met2, met3, met4, met5, met6, met7, met8, met9, met10, met11, met12]

# Vérifier si les images sont tous de la même forme (shape)
# shapeimg1 = met4.shape
# for i in image_list:
#     if i.shape != shapeimg1:
#         print("Les images ne sont pas de la même taille")
#         print(i)
#         break
#     else:
#         print("Ok!")

#print(metric1, metric2, metric3)

# met_stack = np.stack((tiffs_list[0], tiffs_list[1], tiffs_list[2], tiffs_list[3], tiffs_list[4], tiffs_list[5],
#                       tiffs_list[6], tiffs_list[7], tiffs_list[8], tiffs_list[9], tiffs_list[10], tiffs_list[11]))

met_stack = np.stack(tiffs_list)

# Enlever (4)
# CorHar (2), ED (5), ProfCur (8), TWI (11)


def fonctionDeMet(a):
    metriques_stack = [
                [a[0], a[1], a[3], a[4], a[6], a[7], a[9], a[10]]
                ]
    print(metriques_stack)
    return clf.predict(metriques_stack)

resultat = np.apply_along_axis(fonctionDeMet, 0, met_stack)

print(resultat)

# je déclare tous les drivers
gdal.AllRegister()
# le driver que je veux utiliser GEOTIFF
driver = gdal.GetDriverByName("GTiff")

# taille de mon image (ce sera la taille de la matrice)
rows = resultat.shape[1]
cols = resultat.shape[2]

# je déclare mon image
# il faut : la taille, le nombre de bandes et le type de données (ce sera des bytes)

# je déclare mon image
# il faut : la taille, le nombre de bandes et le type de données (ce sera des bytes)
image = driver.Create((os.path.join(root_dir, out_tiffs, nom_fichier)), cols, rows, 1, GDT_Byte)

# je cherche la bande 1
band = image.GetRasterBand(1)

# Je remets la matrice en 2 dimension
result1 = resultat.reshape(resultat.shape[1], resultat.shape[2])

# j'écris la matrice dans la bande
band.WriteArray(result1, 0, 0)

# je vide la cache
band.FlushCache()
band.SetNoDataValue(-99)
# j'efface ma matrice
del resultat
del band
del image





