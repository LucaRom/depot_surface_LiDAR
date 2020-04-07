# -*- coding: utf-8 -*-

"""
Created on Wed Jan 2020
@author: Luca Romanini

"""
# Necessite aussi plusieurs dépendances...

import geopandas as gpd # Plusieurs dépendances ...
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns
import gdal

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.metrics import confusion_matrix
from sklearn.metrics import plot_confusion_matrix
from sklearn.feature_selection import SelectFromModel

# Pour importer un shapefile
# Chemin vers le dossier avec les shapefiles
folder_path = r'E:\OneDrive - USherbrooke\001 APP\Programmation\inputs\raster_input\21_fev_2020'

# On crée la liste des shapefiles
files = os.listdir(folder_path)  # Liste des fichiers dans le dossier "folder"
shp_list = [os.path.join(folder_path, i) for i in files if i.endswith('.shp')] # Obtenir une liste des chemins pour
                                                                               # .shp seulement

# On join les fichiers .shp de la liste
new_shp = gpd.GeoDataFrame(pd.concat([gpd.read_file(i) for i in shp_list],
                                     ignore_index = True), crs = gpd.read_file(shp_list[0]).crs)

# On choisi la colonne de que l'on veut prédire (ici le type de dépots)
y_depots = new_shp.zone

# On definit les métriques sur lesquels on veut faire l'analyse
# metriques = ['AvNoVeAnDe', 'CirVarAsp', 'DwnSloInd', 'EdgeDens', 'Pente', 'PlanCurv', 'ProfCurv', 'TPI', 'SphStDevNo', 'TWI', 'TanCurv']
metriques = ['ANVAD', 'CVA', 'DI', 'EdgeDens', 'Pente', 'PlanCur', 'ProfCur', 'TPI', 'SSDN', 'TWI', 'tanCur']
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

################################

import numpy as np
import os
from tifffile import imread
import numpy as np

from osgeo import gdal
from gdalconst import *


# On importe le modèle de classification fait auparavant
''' À Compléter'''

# On définit le dossier parent pour le réutiliser dans l'import d'intrants
root_dir  = os.path.dirname("__file__")
filename = os.path.join(root_dir, 'path/where/to/go')

# Import des images en matrices numpy
tiffs_path = os.path.join(root_dir, 'inputs/tiffs/') # Définition du chemin pour les images
met1 = imread(os.path.join(tiffs_path, 'AvrNorVecAngDev_WB_31H02NE.tif'))
met2 = imread(os.path.join(tiffs_path, 'CirVarAsp_WB_31H02NE.tif'))
met3 = imread(os.path.join(tiffs_path, 'DownslopeInd_WB_31H02NE.tif'))
met4 = imread(os.path.join(tiffs_path, 'EdgeDens_WB_31H02NE.tif'))
met5 = imread(os.path.join(tiffs_path, 'Pente_WB_31H02NE.tif'))
met6 = imread(os.path.join(tiffs_path, 'PlanCur_WB_31H02NE.tif'))
met7 = imread(os.path.join(tiffs_path, 'ProfCur_WB_31H02NE.tif'))
met8 = imread(os.path.join(tiffs_path, 'RelTPI_WB_31H02NE.tif'))
met9 = imread(os.path.join(tiffs_path, 'SphStdDevNor_WB_31H02NE.tif'))
met10 = imread(os.path.join(tiffs_path, 'TWI_WB_31H02NE.tif'))
met11 = imread(os.path.join(tiffs_path, 'tanCur_WB_31H02NE.tif'))


# On crée la liste des metrics pour les itérer
image_list = [met1, met2, met3, met4, met5, met6, met7, met8, met9, met10, met11]

# Vérifier si les images sont tous de la même forme (shape)
shapeimg1 = met1.shape
for i in image_list:
    if i.shape != shapeimg1:
        print("Les images ne sont pas de la même taille")
        print(i)
        break
    else:
        print("Ok!")

#print(metric1, metric2, metric3)

met_stack = np.stack((met1, met2, met3, met4, met5, met6, met7, met8, met9, met10, met11))

def fonctionDeMet(a):
    metriques_stack = [
                [a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9], a[10]]
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
rows, cols = resultat.shape

# je déclare mon image
# il faut : la taille, le nombre de bandes et le type de données (ce sera des bytes)

image = driver.Create("../classi.tiff", cols,rows, 1, GDT_Byte)

# je cherche la bande 1
band = image.GetRasterBand(1)

# j'écris la matrice dans la bande
band.WriteArray(resultat, 0, 0)

# je vide la cache
band.FlushCache()
band.SetNoDataValue(-99)
# j'efface ma matrice
del resultat
del band
del image


#fonctionDeMet(met)

    # metriques = ['ANVAD', 'CVA', 'DI', 'EdgeDens', 'Pente', 'PlanCur', 'ProfCur', 'TPI', 'SSDN', 'TWI', 'tanCur']
    # for i in metriques:
    #     #metrique = met_stack[metriques.index(i),:,:]
    #     met_array.append[]
    # return matrice

# On extrait les dimensions des images
# n_rows = shapeimg1[0]
# m_cols = shapeimg1[1]

# On itere les valeurs des images pour chaque pixel
#for i in range(m_cols - 1):
# for i in range(800, 810):
#     dict_pixel = dict()
#     #for j in range(n_rows - 1):
#     for j in range(800, 810):
#         dict_pixel['metric1'] = metric1[i][j]
#         dict_pixel['metric2'] = metric2[i][j]
#         dict_pixel['metric3'] = metric3[i][j]
#         dict_pixel['metric4'] = metric4[i][j]
#         dict_pixel['metric5'] = metric5[i][j]
#         dict_pixel['metric6'] = metric6[i][j]
#         dict_pixel['metric7'] = metric7[i][j]
#     print(dict_pixel)




