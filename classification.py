# -*- coding: utf-8 -*-

"""
Created on Wed Jan 2020
@author: Luca Romanini

"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from sklearn.tree import DecisionTreeRegressor

# Necessite aussi plusieurs dépendances...

fichier_shp = r'E:\OneDrive - USherbrooke\001 APP\Programmation\inputs\Zone_Depots.shp'
seg_poly = gpd.read_file(fichier_shp)

# seg_poly.plot()
# plt.show()

print(seg_poly.columns) # Montrer le nom des colonnes

# On choisi la colonne que l'on veut prédire (ici le type de dépots)
y_depots = seg_poly(colonne_depot)

# On definit les métriques sur lesquels on veut faire l'analyse
metriques = ['col1', 'col2', 'col3', 'col4']
X = seg_poly[metriques]

print(X.describe())
print(X.head())

