# -*- coding: utf-8 -*-

"""
Created on Wed Jan 2020
@author: Luca Romanini

"""

import geopandas as gpd # Plusieurs dépendances ...
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
import fiona

# Necessite aussi plusieurs dépendances...

fichier_shp = r'E:\OneDrive - USherbrooke\001 APP\Programmation\inputs\tpi_david\zone_depots_glaciolacustre_31H02NE_MTM8.shp'
seg_poly = gpd.read_file(fichier_shp)

# seg_poly.plot()
# plt.show()

#print(seg_poly.columns) # Montrer le nom des colonnes

# On choisi la colonne que l'on veut prédire (ici le type de dépots)
y_depots = seg_poly.CODE_DEPOT

# On definit les métriques sur lesquels on veut faire l'analyse
metriques = ['_count', '_sum', '_mean', '_median', '_stdev', '_min', '_max', '_range', '_minority', '_majority']
X_metriques = seg_poly[metriques]

# print(X_metriques.describe())
# print(X_metriques.head())

# Séparation des données en données d'entrainement et données de tests
train_metriques, test_metriques, train_y, test_y = train_test_split(X_metriques, y_depots, test_size = 0.25, random_state = 42)

# print('Training Features Shape:', train_metriques.shape)
# print('Training Labels Shape:', train_y.shape)
# print('Testing Features Shape:', test_metriques.shape)
# print('Testing Labels Shape:', test_y.shape)

# Create a Gaussian Classifier
clf = RandomForestClassifier(n_estimators = 100, verbose = 2, oob_score = True, random_state = 42)

# Train the model using the training sets y_pred=clf.predict(X_test)
clf.fit(train_metriques, train_y)

y_pred = clf.predict(test_metriques)

# Impression de précision
print("Accuracy:", metrics.accuracy_score(test_y, y_pred))

# Matrice de confusion
#pd.crosstab()

# Creer une nouvelle colonne dans le shapefile
liste_des_resultats = list(zip(test_y, y_pred))
df = pd.DataFrame({'id': test_y.index, 'prediction': y_pred})

# On ajoute les prédictions au futur shapefile
for i, j in seg_poly.iterrows():
    for k, l in df.iterrows():
        if i == l['id']:
            seg_poly.loc[i, 'prediction'] = l['prediction']

# On crée le shapefile avec les prédictions
seg_poly.to_file("result_prediction.shp") # Vérifier fiona




