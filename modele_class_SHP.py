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

# new_shp.plot()
# plt.show()

#print(new_shp.columns) # Montrer le nom des colonnes

# On choisi la colonne de que l'on veut prédire (ici le type de dépots)
y_depots = new_shp.zone

# On definit les métriques sur lesquels on veut faire l'analyse
metriques = ['AvNoVeAnDe', 'CirVarAsp', 'DwnSloInd', 'EdgeDens', 'Pente', 'PlanCurv', 'ProfCurv', 'TPI', 'SphStDevNo', 'TWI', 'TanCurv']
X_metriques = new_shp[metriques]

# X_metriques = csv_metrique.valeur_tpi
# X_metriques = X_metriques.to_numpy()
# X_metriques = X_metriques.reshape(-1, 1)

# Séparation des données en données d'entrainement et données de tests
train_metriques, test_metriques, train_y, test_y = train_test_split(X_metriques, y_depots, test_size = 0.30, random_state = 42)

# Create a Gaussian Classifier
clf = RandomForestClassifier(n_estimators = 500, verbose = 2, oob_score = True, random_state = 42)

# Train the model using the training sets y_pred=clf.predict(X_test)
clf.fit(train_metriques, train_y)

y_pred = clf.predict(test_metriques)

# Impression de précision
print("Accuracy:", metrics.accuracy_score(test_y, y_pred))

# Matrice de confusion
#pd.crosstab()
c_matrice = confusion_matrix(test_y, y_pred)

c_matrice = confusion_matrix(test_y, y_pred)

disp = plot_confusion_matrix(clf, test_metriques, test_y,
                             cmap = plt.cm.Blues,
                             values_format='d')

# Importances des valeurs explicatives (métriques) dans le modèles

# Pour impression dans la console
# for feature in zip(X_metriques, clf.feature_importances_):
#     print(feature)

# Pour impression graphique
importances = clf.feature_importances_
indices = np.argsort(importances) # Tri en orde décroissant

# plot them with a horizontal bar chart
plt.figure() # Crée une nouvelle instance de graphique
plt.title('Importances des métriques')
plt.barh(range(len(indices)), importances[indices], color='b', align='center')
plt.yticks(range(len(indices)), [metriques[i] for i in indices])
plt.xlabel('Importance relative (%)')
plt.show()

# Export des résultats en .shp pour visualisation
# Creer une nouvelle colonne dans le shapefile
liste_des_resultats = list(zip(test_y, y_pred))
df = pd.DataFrame({'id': test_y.index, 'prediction': y_pred})

# # On ajoute les prédictions au futur shapefile
# for i, j in new_shp.iterrows():
#      for k in df.iterrows():
#          print(k)
#         if i == l['id']:
#             new_shp.loc[i, 'prediction'] = l['prediction']

to_export = new_shp.merge(df, on = 'id')

# # On crée le shapefile avec les prédictions
to_export.to_file("result_prediction.shp") # Vérifier fiona

print("fait une correlation entre les metriques")

# Pairplot seaborn
sns.pairplot(new_shp, hue='zone', corner = True, vars = ["DwnSloInd", "Pente", "SphStDevNo", "CirVarAsp", "TWI"])