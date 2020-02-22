# -*- coding: utf-8 -*-

"""
Created on Wed Jan 2020
@author: Luca Romanini

"""
# Necessite aussi plusieurs dépendances...

import geopandas as gpd # Plusieurs dépendances ...
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.metrics import confusion_matrix
from sklearn.metrics import plot_confusion_matrix
from sklearn.feature_selection import SelectFromModel

# Import de .csv
csv_metrique = pd.read_csv(r'E:\OneDrive - USherbrooke\001 APP\Programmation\inputs\31h02se_full_metrics.csv')

#print(seg_poly.columns) # Montrer le nom des colonnes
print(csv_metrique.columns)

# On choisi la colonne que l'on veut prédire (ici le type de dépots)
#y_depots = seg_poly.CODE_DEPOT
y_depots = csv_metrique.Zone

# On definit les métriques sur lesquels on veut faire l'analyse
metriques = ['TPI', 'TWI', 'Pente', 'CircVarAsp']
X_metriques = csv_metrique[metriques]

# X_metriques = csv_metrique.valeur_tpi
# X_metriques = X_metriques.to_numpy()
# X_metriques = X_metriques.reshape(-1, 1)

# Séparation des données en données d'entrainement et données de tests
train_metriques, test_metriques, train_y, test_y = train_test_split(X_metriques, y_depots, test_size = 0.25, random_state = 42)

# Create a Gaussian Classifier
clf = RandomForestClassifier(n_estimators = 100, verbose = 2, oob_score = True, random_state = 42)

# Train the model using the training sets y_pred=clf.predict(X_test)
clf.fit(train_metriques, train_y)

y_pred = clf.predict(test_metriques)

# Impression de précision
print("Accuracy:", metrics.accuracy_score(test_y, y_pred))

# Matrice de confusion
#pd.crosstab()
#c_matrice = confusion_matrix(test_y, y_pred)

c_matrice = confusion_matrix(test_y, y_pred)

disp = plot_confusion_matrix(clf, test_metriques, test_y,
                             cmap = plt.cm.Blues,
                             values_format='d')

# Feature selections
for feature in zip(X_metriques, clf.feature_importances_):
    print(feature)
