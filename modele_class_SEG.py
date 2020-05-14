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
import seaborn as sns

from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics


from sklearn.metrics import confusion_matrix
from sklearn.metrics import plot_confusion_matrix
from sklearn.feature_selection import SelectFromModel
from sklearn.utils import resample

# On définit le dossier parent pour le réutiliser dans l'import d'intrants
root_dir  = os.path.dirname("__file__")

# Pour importer un shapefile
# Chemin vers le dossier avec les shapefiles
folder_path = os.path.join(root_dir, 'inputs/seg_avec_stats/sickit_31H02NE_SE')

# On crée la liste des shapefiles
files = os.listdir(folder_path)  # Liste des fichiers dans le dossier "folder"
shp_list = [os.path.join(folder_path, i) for i in files if i.endswith('.shp')] # Obtenir une liste des chemins pour
                                                                               # .shp seulement

# On join les fichiers .shp de la liste
new_shp_temp = gpd.GeoDataFrame(pd.concat([gpd.read_file(i) for i in shp_list],
                                     ignore_index = True))

#, crs = gpd.read_file(shp_list[0]).crs

# On enleve la colonne 'label' et on enleve les rangées 'nulles'
del new_shp_temp['CorH_media']
del new_shp_temp['CorH_mean']
del new_shp_temp['CorH_std']
del new_shp_temp['ANVAD_coun']
del new_shp_temp['ConH_count']
del new_shp_temp['CorH_count']
del new_shp_temp['CVA_count']
del new_shp_temp['DI_count']
del new_shp_temp['ED_count']
del new_shp_temp['MeaH_count']
del new_shp_temp['PC_count']
del new_shp_temp['Pen_count']
del new_shp_temp['SSDN_count']
del new_shp_temp['TPI_count']
del new_shp_temp['TWI_count']
new_shp_temp = new_shp_temp.dropna()

# Pour tester temporaire... peut être effacé
#new_shp_temp.to_file(os.path.join(root_dir, 'outputs/Segmentations/test_seg_concat01.shp'))


# for i, row in new_shp_temp.iterrows():
#     new_shp_temp[row] = i

# new_shp.plot()
# plt.show()

df_majority = new_shp_temp[new_shp_temp.Zone==0]
df_minority = new_shp_temp[new_shp_temp.Zone==1]

# On enlève les valeur Null (majoritairement issue des métriques de textures)
# df_majority = df_majority.dropna()
# df_minority = df_minority.dropna()

# Downsample majority class
df_majority_downsampled = resample(df_majority,
                                   replace = False,  # sample without replacement
                                   n_samples = len(df_minority),  # to match minority class
                                   random_state = 123)  # reproducible results

# Combine minority class with downsampled majority class
new_shp = pd.concat([df_majority_downsampled, df_minority])

#print(new_shp.columns) # Montrer le nom des colonnes

# On choisi la colonne de que l'on veut prédire (ici le type de dépots)
y_depots = new_shp.Zone

# On definit les métriques sur lesquels on veut faire l'analyse
# metriques = ['AvNoVeAnDe', 'CirVarAsp', 'DwnSloInd', 'EdgeDens', 'Pente', 'PlanCurv', 'ProfCurv', 'TPI', 'SphStDevNo', 'TWI', 'TanCurv']
metriques = list(new_shp.iloc[:,1:58])
# metriques.remove('path')
# metriques.remove('cat')
# metriques.remove('cat')

X_metriques = new_shp[metriques]
#X_metriques = X_metriques.dropna()

#np.any(np.isnan(X_metriques))      #Test NaN ou Infinit
#np.all(np.isfinite(X_metriques))

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

disp.ax_.set_title('Matrice de confusion - Statistiques Zonales')
plt.xlabel('Réel')
plt.ylabel('Prédit')

# Pour impression graphique
importances = clf.feature_importances_
indices = np.argsort(importances)
indices = indices[:20]

# plot them with a horizontal bar chart
plt.figure() # Crée une nouvelle instance de graphique
plt.title('Importances des métriques')
plt.barh(range(len(indices)), importances[indices], color='b', align='center')
plt.yticks(range(len(indices)), [metriques[i] for i in indices])
plt.xlabel('Importance relative (%)')
plt.show()


# Prediction complète
metriques_zone_complete = new_shp_temp[metriques] # On repart avec tous les polygones
# full_pred = clf.predict(metriques_zone_complete)
# full_pred = pd.DataFrame(full_pred)

new_shp_temp['prediction'] = clf.predict(metriques_zone_complete)

#new_shp_test = pd.concat([new_shp_temp, full_pred], axis=0, ignore_index=True)

#new_shp_temp['prediction'] = full_pred.iloc[:, :1]
#new_shp_temp['prediction'] = full_pred[:]

##### ATTENTION POTENTIELLEMENT PAS BON, LAISSEZ POUR AUTRE CHOSE #####

# Export des résultats en .shp pour visualisation
# Creer une nouvelle colonne dans le shapefile
# liste_des_resultats = list(zip(test_y, y_pred))
# df = pd.DataFrame({'ID': test_y.index, 'prediction': y_pred})
#
# #to_export_2 = new_shp_temp.merge(df, on = 'ID')
# to_export_2 = new_shp_temp.merge(df, how = 'left', left_index = True, right_index = True)

#### FIN ####


# #new_full_raster = pd.concat([full_raster, pd.DataFrame(full_pred)], axis=0, ignore_index=True)


# On crée le shapefile avec les prédictions
date_classi = str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) #On ajoute la date au fichier pour suivre nos tests
nom_fichier = 'result_prediction_SEG' + date_classi + '.shp'
#new_shp_test.to_file(os.path.join(root_dir, 'outputs/Segmentations', nom_fichier))
new_shp_temp.to_file(os.path.join(root_dir, 'outputs/Segmentations', nom_fichier))


# # Export des résultats en .shp pour visualisation
# # Creer une nouvelle colonne dans le shapefile
# liste_des_resultats = list(zip(test_y, y_pred))
# df = pd.DataFrame({'id': test_y.index, 'prediction': y_pred})
#
# # # On ajoute les prédictions au futur shapefile
# to_export = new_shp.merge(df, on = 'id')

# # On crée le shapefile avec les prédictions
# to_export.to_file("result_prediction.shp") # Vérifier fiona


# # Pairplot seaborn
# allo = sns.pairplot(new_shp, hue='zone', vars=["DwnSloInd", "Pente", "SphStDevNo", "CirVarAsp", "TWI"])
#
# Correlation
# corr = new_shp[metriques].corr()
# fig = plt.figure()
# ax = fig.add_subplot(111)
# cax = ax.matshow(corr,cmap='coolwarm', vmin=-1, vmax=1)
# fig.colorbar(cax)
# ticks = np.arange(0,len(new_shp[metriques].columns),1)
# ax.set_xticks(ticks)
# plt.xticks(rotation=90)
# ax.set_yticks(ticks)
# ax.set_xticklabels(new_shp[metriques].columns)
# ax.set_yticklabels(new_shp[metriques].columns)
# plt.show()