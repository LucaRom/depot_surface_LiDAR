# import rasterio
import fiona
# import rasterio.mask
# import matplotlib.pyplot as plt
# import random
import whitebox
import os
# import numpy as np
# import math
# import pandas as pd
# from scipy import stats
# import statistics as s
# from rasterio import features
# import pprint
# import sys
# from osgeo import gdal
# from osgeo import ogr
import geopandas as gpd
import glob


wbt = whitebox.WhiteboxTools()
wbt.verbose = False

path_metr = r'C:\Users\home\Documents\Documents\APP2\Metriques\31H02\31H02SE'
couche_point = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\inputs\Ech_31H02SE.shp'
# couche_test = r'D:\DATA\shapefile\point_alea.shp'
# path_mnt = r'D:\DATA\MNT_5x5_cor\22G14\MNT_5x5_cor_22G14NE.tif'

# print('Production des points...')
# wbt.raster_to_vector_points(path_mnt, couche_point)
# print('Terminé')
#
#
def extract_value_metrique(path_couche_point, path_metrique):

    print('lecture des métriques...')
    ls = glob.glob(path_metrique + os.sep + '*.tif')
    dic_metrique = {'AvrNorVecAngDev': 'ANVAD', 'CirVarAsp': 'CVA', 'DownslopeInd': 'DI', 'EdgeDens': 'EdgeDens', 'Pente':
            'Pente', 'PlanCur': 'PlanCur', 'ProfCur': 'ProfCur', 'RelTPI': 'TPI', 'SphStdDevNor': 'SSDN', 'tanCur': 'tanCur',
            'TWI': 'TWI'}

    dic_ordre = {}

    print('préparation de la chaine de métriques...')
    chaine_metrique=''
    for i in range(len(ls)):
        metrique = ls[i]
        nom_basename = os.path.basename(metrique).split('_')[0]
        name = dic_metrique[nom_basename]
        dic_ordre.update({str(i+1):name})

        if chaine_metrique == '':
            chaine_metrique = metrique
        else:
            chaine_metrique = chaine_metrique + ';' + metrique

    print(dic_ordre)
    print()

    print('Extraction des valeurs...')
    wbt.extract_raster_values_at_points(chaine_metrique, points=path_couche_point)
    print('Terminé')

    print('Ouverture du SHP...')
    shp = gpd.read_file(path_couche_point)
    # del shp['VALUE']
    print('termine')

    print('Création des nouvelles colonnes...')
    for col in shp.columns:
        if col == 'id' or col == 'geometry':
            pass
        elif col[0:5] == 'VALUE':
            num = col[5:]
            nom_colonne = dic_ordre[num]
            shp[nom_colonne] = shp[col].round(4)
    print('Terminé')

    print('Suppression des anciennes colonnes...')
    for col in shp.columns:
        if col[0:5] == 'VALUE':
            del shp[col]
    print('Terminé')

    print('Sauvegarde...')
    shp.to_file(path_couche_point)
    print('Terminé')


extract_value_metrique(couche_point, path_metr)

# ech = r'D:\DATA\Segmentations\OneDrive_4_08-03-2020\MNT_5x5_cor_31H02NE_SE_Watershed_Merge_stats.shp'
#
# dic_metrique = {'AvNoVeAnDe': 'ANVAD', 'CirVarAsp': 'CVA', 'DwnSloInd': 'DI', 'EdgeDens': 'EdgeDens', 'Pente':
#     'Pente', 'PlanCurv': 'PlanCur', 'ProfCurv': 'ProfCur', 'TPI': 'TPI', 'SphStDevNo': 'SSDN', 'TanCurv': 'tanCur',
#                 'TWI': 'TWI'}
#
# print('Lecture...')
# shp = gpd.read_file(ech)
# print('Traitement')
# for col in shp.columns:
#     if col == 'ID' or col == 'geometry' or col == 'zone' or col == 'path' or col == 'layer':
#         pass
#     else:
#         nom_metrique = col.split('_')[0]
#         reste = col.split('_')[1]
#         #nom = dic_metrique[col]
#         if nom_metrique == 'TanCur':
#             nom = 'tanCur_{}'.format(reste)
#             shp[nom] = shp[col]
#             del shp[col]
#         elif nom_metrique == 'ED':
#             nom = 'EdgeDens_{}'.format(reste)
#             shp[nom] = shp[col]
#             del shp[col]
#
# print('sauvegarde')
# shp.to_file(ech)
# for col in shp.columns:
#     print(col)





#     liste_metrique = glob.glob(path_metrique + os.sep + '*.tif')
#     dic_metrique = {'AvrNorVecAngDev': 'ANVAD', 'CirVarAsp': 'CVA', 'DownslopeInd': 'DI', 'EdgeDens': 'EdgeDens', 'Pente':
#         'Pente', 'PlanCur': 'PlanCur', 'ProfCur': 'ProfCur', 'RelTPI': 'TPI', 'SphStdDevNor': 'SSDN', 'tanCur': 'tanCur',
#         'TWI': 'TWI'}
#
#     print('Ouverture de la couche de points...')
#     shp = gpd.read_file(path_couche_point)
#     print('Terminé')
#     for metrique in liste_metrique:
#         nom_basename = os.path.basename(metrique).split('_')[0]
#         print('Métrique: {}'.format(nom_basename))
#         name = dic_metrique[nom_basename]
#
#         print('Extraction des valeurs...')
#         wbt.extract_raster_values_at_points(metrique, path_couche_point)
#         print('Terminé')
#
#         print('Réouverture du SHP...')
#         shp1 = gpd.read_file(path_couche_point)
#         print('Terminé')
#
#         print('Création de la nouvelle colonne...')
#         shp[name] = shp1['VALUE1'].round(4)
#         print('Terminé')
#
#         # print("Suppression de l'ancienne colonne...")
#         # del shp['VALUE1']
#         # print('Terminé')
#
#     print('Sauvegarde de la couche...')
#     shp.to_file(path_couche_point)
#     print('Terminé')
#
#     print(shp)
#
#
# extract_value_metrique(couche_point, path_metr)




# Suppression des colonnes créées
# shp = gpd.read_file(couche_test)
#
# for col in shp.columns:
#     if col == 'id' or col == 'geometry':
#         pass
#     else:
#         del shp[col]
# shp.to_file(couche_test)
# print(shp)




# import sys
# import os
#
# sys.path.append(r'C:\OSGeo4W64\apps\qgis-ltr\python')
# os.environ['PATH'] += r'C:\OSGeo4W64\apps\qgis-ltr\bin'
# os.environ['PATH'] += r'C:\OSGeo4W64\apps\Qt5\bin'
#
# print(os.environ)
#
# from qgis.core import *
# print('done')
# path_mask = r'D:\test_mask_binaire.tif'
# path_qgis = r'C:\ProgramData\Anaconda3\envs\GDAL_test\Library\python\qgis'
# path_mnt = r'D:\DATA\MNT\31H02\MNT_31H02NE.tif'
# # path_mnt = r'D:\DATA\MNT_5x5_corr\31H02\MNT_5x5_corr_31H02NE.tif'





# wb = whitebox.WhiteboxTools()
#
# tpi = os.path.join(os.path.dirname(path_mnt), 'TPI_31H02NO.tif')
# wb.relative_topographic_position(path_mnt, tpi, 40)


# # ouverture du mnt original
# mnt_original = gdal.Open(path_mnt, gdal.GA_Update)
# original_band = mnt_original.GetRasterBand(1)
#
# # Valeur NoData du mnt original
# nodata_value = original_band.GetNoDataValue()
# print('La valeur no data est: {}'.format(nodata_value))

# # Lissage du mnt original
# path_mnt_lisse = r'D:\smooth.tif'
# wb.feature_preserving_smoothing(path_mnt, path_mnt_lisse)
#
# # ouverture du mnt lissé
# mnt_filtre = gdal.Open(path_mnt_lisse, gdal.GA_Update)
# lisse_band = mnt_filtre.GetRasterBand(1)
#
# # Déclaration de la valeur nodata dans le fichier output
# lisse_band.SetNoDataValue(nodata_value)
# lisse_nodata_value = lisse_band.GetNoDataValue()
# print('La valeur no data est: {}'.format(lisse_nodata_value))


# Ne fonctionne pas.



# sys.path.append(path_qgis)
# from qgis.core import *
#
#
# gdal.UseExceptions()
#
# #
# #  get raster datasource
# #
#
# type_mapping = {gdal.GDT_Byte: ogr.OFTInteger,
#                 gdal.GDT_UInt16: ogr.OFTInteger,
#                 gdal.GDT_Int16: ogr.OFTInteger,
#                 gdal.GDT_UInt32: ogr.OFTInteger,
#                 gdal.GDT_Int32: ogr.OFTInteger,
#                 gdal.GDT_Float32: ogr.OFTReal,
#                 gdal.GDT_Float64: ogr.OFTReal,
#                 gdal.GDT_CInt16: ogr.OFTInteger,
#                 gdal.GDT_CInt32: ogr.OFTInteger,
#                 gdal.GDT_CFloat32: ogr.OFTReal,
#                 gdal.GDT_CFloat64: ogr.OFTReal}
#
# dataset = gdal.Open(path_mask)
# srcband = dataset.GetRasterBand(1)
# prj = dataset.GetProjection()
# dst_layername = r'D:\test_mask_poly'
# drv = ogr.GetDriverByName("ESRI Shapefile")
# dst_ds = drv.CreateDataSource( dst_layername + ".shp" )
# srs = ogr.osr.SpatialReference(wkt=prj)
#
# dst_layer = dst_ds.CreateLayer(dst_layername, srs=srs)
# raster_field = ogr.FieldDefn('id', type_mapping[srcband.DataType])
# a = gdal.Polygonize(srcband, None, dst_layer, -1, [], callback=None)






























# Extractions des statistiques


# path_data  = r'D:\DATA\echantillons_metriques'
# path_output = r'D:\DATA\echantillons_metriques\stats_31H02NE.csv'
#
#
# index = ['Min int', 'Min ext', 'Max int', 'Max ext', 'Moyenne int', 'Moyenne ext', 'Écart type int', 'Écart type ext',
#          'Médiane int', 'Médiane ext', 'Skewness int', 'Skewness ext', 'Kurtosis int', 'Kurtosis ext']
#
# data = pd.DataFrame(index=index)
#
#
# for file in os.listdir(path_data):
#
#     nom = file.split('_')[0]
#     csv = os.path.join(path_data, file)
#     df = pd.read_csv(csv, index_col=False)
#
#     out_zone = df['out_zone']
#     in_zone = df['in_zone']
#
#     max_in = in_zone.max()
#     max_out = out_zone.max()
#
#     min_in = in_zone.min()
#     min_out = out_zone.min()
#
#     mean_in = s.mean(in_zone)
#     mean_out = s.mean(out_zone)
#
#     sd_in = s.stdev(in_zone)
#     sd_out = s.stdev(out_zone)
#
#     med_in = s.median(in_zone)
#     med_out = s.median(out_zone)
#
#     skew_in = stats.skew(in_zone)
#     skew_out = stats.skew(out_zone)
#
#     kurt_in = stats.kurtosis(in_zone)
#     kurt_out = stats.kurtosis(out_zone)
#
#     col = [min_in, min_out, max_in, max_out, mean_in, mean_out, sd_in, sd_out, med_in, med_out, skew_in, skew_out,
#            kurt_in, kurt_out]
#
#     data[nom] = col
#
# print(data)
# data.to_csv(path_output)
#







# with rasterio.open(path) as metrique:
#     image = metrique.read(1, out_shape=(1, metrique.height, metrique.width))
#
#     for ligne in image:
#         print(ligne)
#     print()

# Échantillonnage aléatoire stratifié systématique

# liste = []
# liste_choix = []
# taille = 20
# index_col = 0
# index_ligne = 0
#
# # On parcours la grille le nombre de fois que la fenêtre choisie rentre
# for j in range(int(metrique.height/taille)):
#     for i in range(int(metrique.width/taille)):
#
#         # On défini un range de ligne et de colonne correspondant à la taille de la grille en partant d'en haut à gauche
#         for ligne in range(index_ligne, index_ligne + taille):
#             for indexes in range(index_col, index_col + taille):
#                 # Pour chaque pixel dans la fenêtre définie, on l'ajoute dans une liste
#                 liste.append(image[ligne][indexes])
#         else:
#             # Une fois tous les pixels de la fenêtre dans la liste, on en choisit 1 au hasard qu'on ajoute à la liste de tous les pixels choisis
#             print(liste)
#             choix = random.choice(liste)
#             liste_choix.append(choix)
#
#             # S'il reste encore assez de ligne à la grille, on se déplace d'une taille de fenêtre vers le bas jusqu'à la fin de la grille
#             if metrique.height >= (index_ligne + taille):
#                 index_ligne += taille
#                 liste = []
#     else:
#         # Si on a atteint le nombre max de ligne pour descendre,
#         # S'il reste assez de colonne dans la grille, on recommence le processus, mais 1 taille de fenêtre plus à droite jusqua'à la fin de la grille
#         if metrique.width >= (index_col + taille):
#             index_col += taille
#             index_ligne = 0
#
# print(liste_choix)
# #















