# import geopandas as gpd
# import random
# from fiona.crs import from_epsg
# from shapely.geometry import shape, Point, Polygon
# from shapely.ops import nearest_points
# import pandas as pd
#import whitebox
# import glob
from fonctions_metriques import Downslope_Ind, SCA, textures_glcm, AverNormVectAngDev
from pretraitements import resampling_cubic_spline
from osgeo import gdal

path = r'C:\Users\home\Documents\Documents\APP3\mnt_buffer\31H02NE_buffer.tif'
DI = r'C:\Users\home\Documents\Documents\APP3\mnt_buffer\test_dslp_ind.tif'
sca = r'C:\Users\home\Documents\Documents\APP3\mnt_buffer\test_sca.tif'
buff50 = r'C:\Users\home\Documents\Documents\APP3\mnt_buffer\31H02NE_buffer_50.tif'
mean = r'C:\Users\home\Documents\Documents\APP3\mnt_buffer\mean.tif'
cor = r'C:\Users\home\Documents\Documents\APP3\mnt_buffer\cor.tif'
cont = r'C:\Users\home\Documents\Documents\APP3\mnt_buffer\cont.tif'
# Chemin vers l'application 'Rscript.exe'
path_r = r"C:\Program Files\R\R-3.6.3\bin\Rscript.exe"
# Chemin vers le script 'haralick.R'
path_script = r"C:\Users\home\Documents\Documents\APP2\haralick.R"
moy = r'C:\Users\home\Documents\Documents\APP3\metriques\31H02\31H02NE\MeaH_GLCM_31H02NE.tif'
anvad = r'C:\Users\home\Documents\Documents\APP3\mnt_buffer\anvad.tif'
#resampling_cubic_spline(path, buff50, 2)

# textures_glcm(path_r=path_r, path_script=path_script, input=buff50, output=mean, metrique='1', kernel='3')
# textures_glcm(path_r=path_r, path_script=path_script, input=buff50, output=cor, metrique='2', kernel='3')
# textures_glcm(path_r=path_r, path_script=path_script, input=buff50, output=cont, metrique='3', kernel='3')

AverNormVectAngDev(path, anvad, 40)

# data = gdal.Open(path)
# b = data.GetRasterBand(1)
# nodata = b.GetNoDataValue()
# print(nodata)


# import os
# import glob
# rep_output = r'C:\Users\home\Documents\Documents\APP2\mnt'
# liste_files = ['31H02NE', '31H02SE']
#
# for root, dir, files in os.walk(rep_output):
#     for i in files:
#         print(i)

# liste_path = []
# for root, dir, files in os.walk(path):
#     for i in liste_feuillet:
#         liste_path.extend(os.path.join(root, j) for j in files if i in j)
# for i in liste_path:
#     print(i)


# Vérification des fichiers déjà présents dans le répertoire
# print('liste des MNT adjacents: {}'.format(liste_files))
# liste_path = []
# deja_present = []
# for root, dir, files in os.walk(rep_output):
#     for i in liste_files:
#         for j in files:
#             if i in j:
#                 deja_present.append(i)
#                 liste_path.append(os.path.join(root, j))
#
# liste_files = [i for i in liste_files if i not in deja_present]
# print('liste des MNT à télécharger: {}'.format(liste_files))

### CREATION DU BUFFER AUTOUR DES RASTER À L'AIDE D'UNE MOSAIQUE###

# from osgeo import gdal
# import rasterio, rasterio.mask
# from rasterio.merge import merge
# from rasterio.plot import show
# import glob
# import os
# from fonctions_metriques import resampling_cubic_spline
# from ech_pixel import raster_calculation, creation_raster, creation_buffer, conversion_polygone, delete_border
#

# def creation_mosaique(liste_mnt, output):
#
#     # Création d'une classe de liste pouvant être accédée par un "with"
#     class liste_mosaic(list):
#         def __enter__(self):
#             return self
#         def __exit__(self, *a):
#             print('')
#
#     # Ouverture des raster avec rasterio
#     with liste_mosaic(rasterio.open(mnt) for mnt in liste_mnt) as liste_mosaic:
#         # Création de la mosaique
#         mosaique, out_trans = merge(liste_mosaic)
#         # Affichage de la mosaique
#         #show(mosaique, cmap='terrain')
#         out_meta = liste_mosaic[0].meta.copy()
#         # Update les metadata
#         out_meta.update({"driver": "GTiff",
#                          "height": mosaique.shape[1],
#                           "width": mosaique.shape[2],
#                           "transform": out_trans,
#                           "crs": "EPSG:2950"
#                           }
#                         )
#
#         # Écriture du fichier de sortie
#         with rasterio.open(output, "w", **out_meta) as dest:
#              dest.write(mosaique)
#              dest.close()
#
#         # Fermeture des fichiers ouverts
#         for files in liste_mosaic:
#             files.close()
#
# # # Suppression des fichiers temporaires
# # for files in liste_resample:
# #     os.remove
#
#
# # Répertoire intrant et sortant
# path_mnt = r'C:\Users\home\Documents\Documents\APP2\mnt\31H02NE'
# feuillet = '31H02NE'
# distance = 1000
# output_mosaique = os.path.join(path_mnt, '{}_mosaique.tif'.format(os.path.basename(path_mnt)))
# output_mnt_buff = os.path.join(path_mnt, '{}_buffer.tif'.format(os.path.basename(path_mnt)))
#
# #
# # # Liste des MNT dans le répertoire intrant
# # liste_mnt = [fn for fn in glob.glob(os.path.join(path_mnt, '*.tif'))
# #          if 'mosaique' not in os.path.basename(fn)]
# # print(liste_mnt)
# #
# # # Resampling
# # liste_resample = []
# # for i in liste_mnt:
# #     name = '{}_resample.tif'.format(os.path.basename(i)[:-4])
# #     resampled = os.path.join(path_mnt, name)
# #     resampling_cubic_spline(i, resampled, 50)
# #     liste_resample.append(resampled)
# # print(liste_resample)
# #
# # creation_mosaique(liste_resample, output)
# #mnt = os.path.join(path_mnt, 'MNT_{}_resample.tif'.format(feuillet))
#
#
# def creation_buffer_raster(input_raster, input_mosaic, output):
#
#     # Transormation du MNT en en valeurs 0 pour simplifier la polygonisation
#     mnt0 = raster_calculation(input_raster)
#
#     # Création d'un raster en mémoire
#     mnt0_raster = creation_raster(mnt0, input_raster)
#
#     # Conversion en polygone dans un couche en mémoire et suppression des bordures
#     path_couche_memory = "/vsimem/mnt0_poly.shp"
#     mnt0_poly = conversion_polygone(mnt0_raster, path_couche_memory)
#     cadre = delete_border(path_couche_memory)
#     epsg = int(str(cadre.crs).split(':')[1])
#
#     # Création du buffer autour du cadre
#     buff = creation_buffer(cadre, distance, epsg, 3, 2)
#     buff.to_file(os.path.join(path_mnt, 'test_buffer.shp'))
#     path_buff = "/vsimem/buffer.shp"
#     buff.to_file(path_buff)
#
#     # Clip de la mosaique au buffer
#     clip = gdal.Warp(output, input_mosaic, cutlineDSName=path_buff)

### VIEILLE FONCTION SELECTION MNT###
# def liste_mnt_a_download(feuillet, div_debut, div_fin):
#
#     liste_voulu = []
#     if feuillet[:3] == div_debut[:3] and feuillet[:3] == div_fin[:3]:
#
#         nb_deb = int(div_debut[3:5])
#         nb_fin = int(div_fin[3:5])
#         nb_fois = nb_fin - nb_deb + 1
#
#         compte_feuillet = nb_deb
#         for i in range(nb_fois):
#             liste_div = ['NE','NO','SE','SO']
#             for j in liste_div:
#                 compte = None
#                 if compte_feuillet < 10:
#                     compte = '0'+ str(compte_feuillet)
#                 else:
#                     compte = str(compte_feuillet)
#
#                 a = '{}{}{}'.format(feuillet, compte, j)
#                 liste_voulu.append(a)
#             compte_feuillet += 1
#
#         return liste_voulu

# ### RASTERIZE BUFFER ###
# import geopandas as gpd
# from osgeo import ogr, gdal, osr
# from osgeo.gdalnumeric import *
# from osgeo.gdalconst import *
# from osgeo import ogr
#
# path_shp = r'C:\Users\home\Documents\Documents\APP3\buffer_mnt.shp'
# path_mnt = r'C:\Users\home\Documents\Documents\APP2\MNT_31H02NE_5x5.tif'
# output = r'C:\Users\home\Documents\Documents\APP3\test_rasterize.tif'
#
# # Extrait les attributs du MNT
# raster = gdal.Open(path_mnt)
# geo = raster.GetGeoTransform()
# Xcell_size=int(abs(geo[1]))
# Ycell_size=int(abs(geo[5]))
# proj = raster.GetProjection()
# band = raster.GetRasterBand(1)
# nodata = band.GetNoDataValue()
#
# # Extraction des limites du shp avec OGR
# source_ds = ogr.Open(path_shp)
# source_layer = source_ds.GetLayer()
# x_min, x_max, y_min, y_max = source_layer.GetExtent()
# print(x_min, x_max, y_min, y_max)
#
# # Écriture du .tif avec GDAL
# x_res = int((x_max - x_min) / Xcell_size)
# y_res = int((y_max - y_min) / Xcell_size)
# target_ds = gdal.GetDriverByName('GTiff').Create(output, x_res, y_res, 1, gdal.GDT_Byte)
# target_ds.SetGeoTransform((x_min, Xcell_size, 0, y_max, 0, -Xcell_size))
# target_ds.SetProjection(proj)
# band = target_ds.GetRasterBand(1)
# band.SetNoDataValue(nodata)
#
# # Rasterize
# gdal.RasterizeLayer(target_ds, [1], source_layer, burn_values=[1])

# Geopandas
# shp = gpd.read_file(path_shp)
# geom = shp['geometry']
# bbox = list(geom.bounds.values[0])
# x_min, y_min, x_max, y_max = [i for i in bbox]
# print(x_min, x_max, y_min, y_max)




# import numpy as np
# from scipy.signal import convolve2d
#
# data = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                  [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
#                  [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
#                  [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
#                  [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
#                  [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
#                  [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
#                  [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
#                  [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
#                  [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
#                  [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
#                  [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
#                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
#
# from osgeo import gdal
# import numpy as np,sys
#
# def raster_buffer(raster_filepath, dist=1000):
#      """This function creates a distance buffer around the given raster file with non-zero values.
#      The value in output raster will have value of the cell to which it is close to."""
#      d=gdal.Open(raster_filepath)
#      if d is None:
#          print("Error: Could not open image " + raster_filepath)
#          sys.exit(1)
#      global proj,geotrans,row,col
#      proj=d.GetProjection()
#      geotrans=d.GetGeoTransform()
#      row=d.RasterYSize
#      col=d.RasterXSize
#      inband=d.GetRasterBand(1)
#      nodata = inband.GetNoDataValue()
#      in_arr = inband.ReadAsArray(0,0,col,row)
#      in_arr[in_arr == nodata] = 0
#      in_array = in_arr.astype(int)
#      Xcell_size=int(abs(geotrans[1]))
#      Ycell_size=int(abs(geotrans[5]))
#      cell_size = (Xcell_size+Ycell_size)/2
#      cell_dist=dist/cell_size
#      out_array=np.zeros_like(in_array)
#      temp_array=np.zeros_like(in_array)
#      i,j,h,k=0,0,0,0
#      print("Running distance buffer...")
#      while(h<col):
#          k=0
#          while(k<row):
#              if(in_array[k][h]>=1):
#                  i=int(h-cell_dist)
#                  while((i<cell_dist+h) and i<col):
#                      j=int(k-cell_dist)
#                      while(j<(cell_dist+k) and j<row):
#                          if(((i-h)**2+(j-k)**2)<=cell_dist**2):
#                              if(temp_array[j][i]==0 or temp_array[j][i]>((i-h)**2+(j-k)**2)):
#                                  out_array[j][i]= in_array[k][h]
#                                  temp_array[j][i]=(i-h)**2+(j-k)**2
#                          j+=1
#                      i+=1
#              k+=1
#          h+=1
#      d,temp_array,in_array=None,None, None
#      return out_array
#
# def export_array(in_array,output_path):
#     """This function is used to produce output of array as a map."""
#     driver = gdal.GetDriverByName("GTiff")
#     outdata = driver.Create(output_path,col,row,1)
#     outband=outdata.GetRasterBand(1)
#     outband.SetNoDataValue(np.nan)
#     outband.WriteArray(in_array)
#     # Georeference the image
#     outdata.SetGeoTransform(geotrans)
#     # Write projection information
#     outdata.SetProjection(proj)
#     outdata.FlushCache()
#     outdata = None
#
#
# path_mnt = r'C:\Users\home\Documents\Documents\APP2\MNT_31H02SE_5x5.tif'
# output = r'C:\Users\home\Documents\Documents\APP\MNT_31H02SE_5x5_buffer.tif'
#
# import time
# start = time.time()
#
# raster_buffer_array=raster_buffer(path_mnt,100)
# export_array(raster_buffer_array,"Output//buffer.tif")
# print("Done")
#
# # Impression du temps
# end = time.time()
# elapsed = end - start
# print("Elapsed time : %.2f s" % (elapsed))

# arr_valid = data_valid.vstack()
# data_pad = np.pad(data_valid, pad_width=1, mode='constant', constant_values=2)
# print(data_pad)

# kernel = np.ones((5, 5))
# result = np.int64(convolve2d(data, kernel, mode='same') > 0)
# print(result)
# print(result.shape)

### TWI DE SAGA###

# import os
# import subprocess
# from fonctions_traitements import run_command, breachDepression
#
# path_mnt = r'C:\Users\home\Documents\Documents\APP2\MNT_31H02SE_5x5.tif'
# mntBreche = r'C:\Users\home\Documents\Documents\APP3\SE_breche.tif'
#
# breachDepression(path_mnt, mntBreche)
#


#
# path_saga = r'C:\Users\home\Documents\Documents\APP3\saga-7.6.3_x64\saga-7.6.3_x64'
# path_mod = r'C:\Users\home\Documents\Documents\APP3\saga-7.6.3_x64\saga-7.6.3_x64\tools'
# # path = os.environ['PATH']
# # path = path + ';' + path_saga
#
# setPathSaga = 'PATH=%PATH%;{}'.format(path_saga)
# setPathMod = 'SAGA_MLB={}'.format(path_mod)
# twi = 'saga_cmd'
# # run_command(setPathSaga)
# # run_command(setPathMod)
#
#
#
#
# command = [setPathSaga, '&&', 'SET', setPathMod, '&&', twi]
# c = '''
#     echo 'a'
#     echo 'b'
#     echo 'c'
#     '''
#
# process = subprocess.Popen(c, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
# out, err = process.communicate(c.encode('utf-8'))
# print(out.decode('urf8'))



## GLCM DE R###

# import subprocess
#
# path_r = r"C:\Program Files\R\R-3.6.3\bin\Rscript.exe"
# path_script = r"C:\Users\home\Documents\Documents\APP2\haralick.R"
# input = r"C:\Users\home\Documents\Documents\APP2\Metriques50m\31H02\31H02NE\Pente_WB_31H02NE_50m.tif"
# output = r"C:\Users\home\Documents\Documents\APP2\haralick\testR.tif"
# texture = "1"
# kernel = "3"
#
# command = [path_r, path_script, input, output, texture, kernel]
#
#
# def tetures_glcm(path_r, path_script, input, output, texture, kernel):
#     '''
#     Nécessite l'installation de R 3.6 et +.
#     :param path_r: Chemin vers l'application Rscript.exe (str)
#     :param path_script: Chemin vers le script 'haralick.R' (str)
#     :param input: Chemin du MNT à traiter (str)
#     :param output: Chemin du fichier de sortie (str)
#     :param texture: Texture d'haralick à créer (str)
#                     - 1 => moyenne
#                     - 2 => correlation
#                     - 3 => contraste
#     :param kernel: Taille du Kernel (str)
#     :return: Raster de la métrique d'haralick voulue sur le MNT en entrée (.tif)
#     '''
#     # On crée la liste de commande à passer
#     commande = [path_r, path_script, input, output, texture, kernel]
#     run_command(commande)
#
#
# def run_command(command):
#     '''
#     Source:  Kannan Ponnusamy (2015), https://www.endpoint.com/blog/2015/01/28/getting-realtime-output-using-python
#     :param command: Liste de commandes à passer dans le terminal (list)
#     :return: Affiche les output de la console en temps réel tant que le processus n'est pas fini (process.poll() est None)
#     '''
#     # On passe la commande dans le terminal
#     process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
#     while True:
#         # On itère dans le output tant que le code de sortie est None. Si une nouvelle ligne apparaît, on l'affiche
#         output = process.stdout.readline()
#         if output == b'' and process.poll() is not None:
#             # Si le processus se termine, on quitte la boucle
#             break
#         if output:
#             print(output.strip())
#     ExitCode = process.poll()
#     return ExitCode
#
#
# run_command(command)

# from rpy2 import robjects
# from rpy2.robjects.packages import importr
# import rpy2.robjects.packages as rpackages
# from rpy2.robjects.vectors import StrVector
# utils = importr('utils')
# packnames = ('rgdal', 'raster', 'glcm')
#
# names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
# if len(names_to_install) > 0:
#     utils.install_packages(StrVector(names_to_install))
# a =robjects.r('''
# setwd('C:/Users/home/Documents/Documents/APP2')
# path_NE <- 'MNT_31H02NE_5x5.tif'
# path_SE <- 'MNT_31H02SE_5x5.tif'
# path_SO <- 'MNT_31H02SO_5x5.tif'
#
# require(raster)
# require(rgdal)
#
# print('yoyo')
# # Contrast_SO <- glcm(raster(path_SO, layer=1), window = c(3,3), statistics = c('contrast'), shift=list(c(0,1), c(1,1), c(1,0), c(1,-1)))
# # plot(Contrast_SO)
# # writeRaster(Contrast_SO, filename = 'test_python_R.tif', format='GTiff', overwrite = TRUE)
# ''')
# print(a)


# gdal = importr('gdal')
# raster = importr('raster')
# sp = importr('sp')
# glcm = importr('glcm')






# def check_min_distance(point, distance, points):
#     """Check if distance from given point to all other points is greater
#     than given value.
#     """
#     if distance == 0:
#         return True
#
#     if len(points) > 0:
#         uni = points.unary_union
#         nearest = nearest_points(point, uni)
#         if len(nearest) == 0:
#             return True
#         if nearest[1].distance(point) < distance:
#             return False
#
#     return True
#
# poly = gpd.read_file(path)
# epsg = int(poly.crs['init'].split(':')[1])
# sample = gpd.GeoDataFrame()
# sample['geometry'] = None
# sample['id'] = None
# sample.crs = from_epsg(epsg)
#
# total = 100.0 / len(poly) if len(poly) else 0
# for ind, row in poly.iterrows():
#     geom = row['geometry']
#     bbox = shape(geom).bounds
#     # if minDistance:
#     #     index = sample.sindex
#     # points = dict()
#     nPoints = 0
#     nIterations = 0
#     maxIterations = value * 50
#     feature_total = total / value if value else 1
#
#     random.seed()
#     pointId = 0
#     while nIterations < maxIterations and nPoints < value:
#
#         height = bbox[3] - bbox[1]
#         width = bbox[2] - bbox[0]
#         rx = bbox[0] + width * random.random()
#         ry = bbox[1] + height * random.random()
#
#         p = Point(rx, ry)
#         # geom = QgsGeometry.fromPointXY(p)
#         if p.within(geom) and \
#                 (not minDistance or check_min_distance(p, minDistance, sample)):
#             sample.loc[nPoints, 'geometry'] = p
#             sample.loc[nPoints, 'id'] = pointId
#             print(sample)
#
#             # f = QgsFeature(nPoints)
#             # f.initAttributes(1)
#             # f.setFields(fields)
#             # f.setAttribute('id', pointId)
#             # f.setGeometry(geom)
#             # sink.addFeature(f, QgsFeatureSink.FastInsert)
#             # points[nPoints] = p
#             nPoints += 1
#             pointId += 1
#             # feedback.setProgress(current_progress + int(nPoints * feature_total))
#         nIterations += 1
#         print(nIterations)
#
#     if nPoints < value:
#         print('Could not generate requested number of random points. Maximum number of attempts exceeded.')
#
# sample.to_file(r'C:\Users\home\Documents\Documents\APP3\test_points.shp')


# orig = Point(1, 1.67)
# origin = gpd.GeoDataFrame()
# origin['geometry'] = None
# origin.loc[0, 'geometry'] = orig
#
# destin = gpd.GeoDataFrame()
# destin['geometry'] = None
# liste_point = [Point(1, 1.45), Point(2, 2), Point(0, 2.5)]
# for i in range(3):
#     destin.loc[i, 'geometry'] = liste_point[i]
#
# union = destin.unary_union
# print(union)
# near = nearest_points(orig, union)
# print(list(near)[1])
# print(near[1].distance(orig))

## ESSAI D'OPTIMISATION AVEC UN INDEX SPATIAL ##

# poly = Polygon([(0, 0), (5, 0), (5, 5), (0,5)])
# pol = gpd.GeoDataFrame(columns=['geometry'])
# pol.loc[0, 'geometry'] = poly
# bbox = shape(poly).bounds
# destin = gpd.GeoDataFrame()
# destin['geometry'] = None
# liste_point = [Point(1, 1.45), Point(6, 6), Point(1, 2.5)]
# for i in range(3):
#     destin.loc[i, 'geometry'] = liste_point[i]
#
# index = destin.sindex
# # ax = pol.plot(color='red', edgecolor='black', alpha=0.5)
# # ax = destin.plot( color='blue', markersize=20, alpha=1)
# # plt.show()
#
# point = Point(3,3)
# #print(destin.within(pol['geometry'].iloc[0]))
# union = destin.unary_union
# #print(nearest_points(point, union)[1])
#
# polygone = pol.loc[pol['geometry']==poly]
# bounds = list(polygone.bounds.values[0])
# intersect = list(index.intersection(bounds))
#
# point_candidates = destin.loc[intersect]
# print(point_candidates)

#
# def check_min_distance(point, distance, points):
#
#     if distance == 0:
#         return True
#     if len(points) > 0:
#         uni = points.unary_union
#         nearest = nearest_points(point, uni)
#         if len(nearest) == 0:
#             return True
#         if nearest[1].distance(point) < distance:
#             return False
#     return True
#
#
# #@profile
# def echantillon_pixel(poly, minDistance, value, epsg, zone):
#
#     #poly = gpd.read_file(input)
#     sample = gpd.GeoDataFrame(columns=['geometry', 'id', 'Zone'])
#     sample.crs = from_epsg(epsg)
#
#     for ind, row in poly.iterrows():
#         geom = row['geometry']
#         bbox = geom.bounds
#         index = sample.sindex
#         nPoints = 0
#         nIterations = 0
#         maxIterations = value * 5
#
#         random.seed()
#         pointId = 0
#         while nIterations < maxIterations and nPoints < value:
#
#             height = bbox[3] - bbox[1]
#             width = bbox[2] - bbox[0]
#             rx = bbox[0] + width * random.random()
#             ry = bbox[1] + height * random.random()
#
#             p = Point(rx, ry)
#
#             if p.within(geom) and (not minDistance or check_min_distance(p, minDistance, sample)):
#                     sample.loc[nPoints, 'geometry'] = p
#                     sample.loc[nPoints, 'id'] = pointId
#                     sample.loc[nPoints, 'Zone'] = zone
#                     nPoints += 1
#                     pointId += 1
#             nIterations += 1
#             if nIterations % 1000 == 0:
#                 print(nIterations)
#
#         if nPoints < value:
#             print(sample)
#             print('Could not generate requested number of random points. Maximum number of attempts exceeded.')
#
#     return sample
#
#
# def dissolve(geodataframe, epsg):
#     if len(geodataframe) > 1:
#         diss = geodataframe.unary_union
#         shpDiss = gpd.GeoDataFrame(columns=['geometry'])
#         shpDiss.loc[0, 'geometry'] = diss
#         shpDiss.crs = from_epsg(epsg)
#         return shpDiss
#     return geodataframe
#
# ## RASTER CALCULATION ##
#
# def raster_calculation(path_raster):
#     mnt = gdal.Open(path_raster)
#     b1 = mnt.GetRasterBand(1)
#     arr = b1.ReadAsArray()
#     arr[(arr >= 0)] = 0
#     return arr
#
# def creation_raster (inputArray,inputMet):
#     # On crée une image GEOTIFF en sortie
#     # je déclare tous les drivers
#     gdal.AllRegister()
#     # le driver que je veux utiliser GEOTIFF
#     driver = gdal.GetDriverByName("MEM")
#
#     # taille de mon image (ce sera la taille de la matrice)
#     rows, cols = inputArray.shape
#
#     # je déclare mon image
#     # il faut : la taille, le nombre de bandes et le type de données (ce sera des bytes)
#     image = driver.Create('MEM',cols, rows, 1, GDT_Float64)
#
#     # J'extrais les paramètres d'une métriques pour le positionnement du fichier sortant
#     data = gdal.Open(inputMet)
#
#     # J'applique les paramètres de positionnement
#     geoTransform = data.GetGeoTransform()
#     data = None # On vide la mémoire
#
#     # On donne la coordonnée d'origine de l'image raster tiré d'une des métriques
#     image.SetGeoTransform(geoTransform)
#
#     # je cherche la bande 1
#     band = image.GetRasterBand(1)
#
#     # Je remets la matrice en 2 dimension
#     # result1 = resultat.reshape(resultat.shape[1], resultat.shape[2])
#     #result1 = inputArray.reshape(inputArray.shape[0], inputArray.shape[1])
#
#     # j'écris la matrice dans la bande
#     # band.WriteArray(result1, 0, 0)
#     band.WriteArray(inputArray, 0, 0)
#
#     # Je définis la projection
#     outRasterSRS = osr.SpatialReference()
#     outRasterSRS.ImportFromEPSG(2950)
#
#     image.SetProjection(outRasterSRS.ExportToWkt())
#
#     # je vide la cache
#     band.FlushCache()
#     band.SetNoDataValue(-99)
#
#     return image
#
#
# def conversion_polygone (dataset, output):
#     gdal.UseExceptions()
#     type_mapping = {gdal.GDT_Byte: ogr.OFTInteger,
#                     gdal.GDT_UInt16: ogr.OFTInteger,
#                     gdal.GDT_Int16: ogr.OFTInteger,
#                     gdal.GDT_UInt32: ogr.OFTInteger,
#                     gdal.GDT_Int32: ogr.OFTInteger,
#                     gdal.GDT_Float32: ogr.OFTReal,
#                     gdal.GDT_Float64: ogr.OFTReal,
#                     gdal.GDT_CInt16: ogr.OFTInteger,
#                     gdal.GDT_CInt32: ogr.OFTInteger,
#                     gdal.GDT_CFloat32: ogr.OFTReal,
#                     gdal.GDT_CFloat64: ogr.OFTReal}
#
#     srcband = dataset.GetRasterBand(1)
#     prj = dataset.GetProjection()
#     dst_layername = os.path.join(output)
#     drv = ogr.GetDriverByName('ESRI Shapefile')
#     dst_ds = drv.CreateDataSource(dst_layername)
#     srs = ogr.osr.SpatialReference(wkt=prj)
#     dst_layer = dst_ds.CreateLayer(dst_layername, srs=srs)
#     raster_field = ogr.FieldDefn('id', type_mapping[srcband.DataType])
#     gdal.Polygonize(srcband, None, dst_layer, -1, [], callback=None)
#
#
# def delete_border(path_shp):
#     df = gpd.read_file(path_shp)
#     df['area'] = [i.area for i in df['geometry']]
#     df = df[df['area'] != df['area'].min()]
#     return df
#
#
# def creation_buffer(geodataframe, distance, epsg):
#     buff = gpd.GeoDataFrame(columns=['geometry'])
#     buff.crs = from_epsg(epsg)
#     buff.loc[0, 'geometry'] = geodataframe.loc[0,'geometry'].buffer(distance, 16)
#     return buff
#
#
# def difference(input, mask, epsg):
#     source = input.loc[0, 'geometry']
#     masque = mask.loc[0, 'geometry']
#     diff = gpd.GeoDataFrame(columns=['geometry'])
#     diff.loc[0, 'geometry'] = source.difference(masque)
#     diff.crs = from_epsg(epsg)
#     return diff
#
#
# def comparaison_area(gdf1, gdf2):
#     area1 = gdf1.loc[0, 'geometry'].area
#     area2 = gdf2.loc[0, 'geometry'].area
#     if area1 < area2:
#         return True
#     else:
#         return False
#
#
# def extract_value_metrique(path_couche_point, path_metrique):
#
#     wbt = whitebox.WhiteboxTools()
#     print('lecture des métriques...')
#     ls = glob.glob(path_metrique + os.sep + '*.tif')
#     dic_metrique = {'AvrNorVecAngDev': 'ANVAD', 'CirVarAsp': 'CVA', 'DownslopeInd': 'DI', 'EdgeDens': 'EdgeDens', 'Pente':
#             'Pente', 'PlanCur': 'PlanCur', 'ProfCur': 'ProfCur', 'RelTPI': 'TPI', 'SphStdDevNor': 'SSDN', 'tanCur': 'tanCur',
#             'TWI': 'TWI', 'Contrast':'ContHar', 'Mean':'MeanHar', 'correl': 'CorHar'}
#
#     dic_ordre = {}
#
#     print('préparation de la chaine de métriques...')
#     chaine_metrique=''
#     for i in range(len(ls)):
#         metrique = ls[i]
#         nom = os.path.basename(metrique).split('_')[0]
#         #name = dic_metrique[nom_basename]
#         dic_ordre.update({str(i+1):nom})
#
#         if chaine_metrique == '':
#             chaine_metrique = metrique
#         else:
#             chaine_metrique = chaine_metrique + ';' + metrique
#
#     print(dic_ordre)
#     print()
#
#     print('Extraction des valeurs...')
#     wbt.extract_raster_values_at_points(chaine_metrique, points=path_couche_point)
#
#     print('Ouverture du SHP...')
#     shp = gpd.read_file(path_couche_point)
#     # del shp['VALUE']
#
#     print('Création des nouvelles colonnes...')
#     for col in shp.columns:
#         if col == 'id' or col == 'geometry':
#             pass
#         elif col[0:5] == 'VALUE':
#             num = col[5:]
#             nom_colonne = dic_ordre[num]
#             shp[nom_colonne] = shp[col].round(4)
#
#     print('Suppression des anciennes colonnes...')
#     for col in shp.columns:
#         if col[0:5] == 'VALUE':
#             del shp[col]
#
#     print('Sauvegarde...')
#     shp.to_file(path_couche_point)
#
#
# def echantillonnage_pix(path_depot, path_mnt, path_metriques, output, nbPoints, minDistance):
#
#
#     # Lecture de la couche de dépôts et extraction du code EPSG
#     print('Lecture et extraction EPSG...')
#     depot = gpd.read_file(path_depot)
#     epsg = int(str(depot.crs).split(':')[1])
#
#     # Regroupement de la couche de dépôts
#     print('Regroupement couche de dépôts...')
#     depot_reg = dissolve(depot, epsg)
#
#     # Multiplier le mnt par 0 pour faciliter la conversion en polygone et création du raster avec le np.array sortant
#     print('Multiplication du MNT par 0...')
#     path_couche_memory = "/vsimem/mnt0_poly.shp"
#     mnt0_array = raster_calculation(path_mnt)
#     mnt0_raster = creation_raster(mnt0_array, path_mnt)
#
#     # Conversion du raster du mnt0 en polygone et supression des bordures pour créer le cadre d'échantillonnage
#     print('Conversion MNT en polygone...')
#     path_couche_memory = "/vsimem/mnt0_poly.shp"
#     conversion_polygone(mnt0_raster, path_couche_memory)
#     print('Suppresion des bordures...')
#     cadre = delete_border(path_couche_memory)
#
#     # Création du buffer autour de la couche de dépôts à la valeur de la distance minimale
#     print('Création du buffer...')
#     buff = creation_buffer(depot_reg, minDistance, epsg)
#
#     # Clip du buffer aux dimension du cadre
#     print('Clip du buffer...')
#     buff_clip = gpd.clip(buff, cadre)
#     #buff_clip.to_file(r'C:\Users\home\Documents\Documents\APP3\buff_clip.shp')
#
#     # Création de la zone extérieure: différence entre le cadre et le buffer clippé
#     print('Création zone externe...')
#     zone_ext = difference(cadre, buff_clip, epsg)
#     #zone_ext.to_file(r'C:\Users\home\Documents\Documents\APP3\difference.shp')
#
#     # Comparaison de superficie entre les dépôts et la zone extérieure pour fixer la limite du nombre de points
#     print('Comparaison...')
#     plus_petite_zone = None
#     plus_grande_zone = None
#     zone = None
#     if comparaison_area(depot_reg, zone_ext):
#         plus_petite_zone = depot_reg
#         plus_grande_zone = zone_ext
#         zone = 1
#         print('Plus petite zone: couche de dépôts ')
#     else:
#         plus_petite_zone = zone_ext
#         plus_grande_zone = depot_reg
#         zone = 0
#         print('Plus petite zone: zone extérieure')
#
#     # Échantillonnage de la plus petite zone
#     print('Échantillonnage petite zone...')
#     ech_petite_zone = echantillon_pixel(plus_petite_zone, minDistance, nbPoints, epsg, zone)
#     #ech_petite_zone.to_file(r'C:\Users\home\Documents\Documents\APP3\ech_petite_zone.shp')
#
#     # Échantillonnage de la plus grande zone selon le nombre de points contenu dans la petite zone
#     if zone == 1:
#         zone = 0
#     elif zone == 0:
#         zone = 1
#     print('Échantillonnage grande zone...')
#     nbPoints_petite = len(ech_petite_zone)
#     ech_grande_zone = echantillon_pixel(plus_grande_zone, minDistance, nbPoints_petite, epsg, zone)
#     #ech_grande_zone.to_file(r'C:\Users\home\Documents\Documents\APP3\ech_grande_zone.shp')
#     print('Terminé')
#
#     # Combinaison des deux zones
#     print('Combinaison des échantillons...')
#     ech_total = gpd.GeoDataFrame(pd.concat([ech_petite_zone, ech_grande_zone], ignore_index=True), crs=from_epsg(epsg))
#     ech_total.to_file(output)
#
#     # Extraction des valeurs des métriques
#     print('Extraction des valeurs des métriques')
#     extract_value_metrique(output, path_metriques)
#     print('Terminé')
#
#
# if __name__ == "__main__":
#
#     # Chemins des couches du MNT et de la couche de dépôts
#     path_depot = r'C:\Users\home\Documents\Documents\APP2\depots_31H02\zone_depots_glaciolacustre_31H02NE_MTM8_reg.shp'
#     path_mnt = r'C:\Users\home\Documents\Documents\APP2\MNT_31H02NE_5x5.tif'
#     path_metriques = r'C:\Users\home\Documents\Documents\APP2\Metriques\31H02\31H02NE'
#     output = r'C:\Users\home\Documents\Documents\APP3\ech_total.shp'
#
#     echantillonnage_pix(path_depot=path_depot, path_mnt=path_mnt, path_metriques=path_metriques,
#                         output=output, nbPoints=2000, minDistance=500)


### VIEUX ECHANTILLONNAGE###

# import rasterio
# import fiona
# import rasterio.mask
# import matplotlib.pyplot as plt
# import whitebox
# import os
# import math
# import numpy as np
#
# def enregistrement_masque(masque_ext_array, masque_zone_array, out_meta, out_transform_ext, out_transform_zones,
#                           dossier_output):
#     # Liste des array des masques avec leur out_transform correspondant
#     liste_masque = [[masque_ext_array, out_transform_ext], [masque_zone_array, out_transform_zones]]
#
#     liste_path = []
#     suffixe = ''
#
#     # Sauvegarde de chaque masque de la liste sous format .tif dans le répertoire en entrée
#     for i in range(len(liste_masque)):
#
#         masque = liste_masque[i][0]
#         out_transform = liste_masque[i][1]
#
#         if i == 0:
#             suffixe = 'ext'
#         elif i == 1:
#             suffixe = 'zones'
#
#         out_meta.update({"driver": "GTiff",
#                          "height": masque.shape[1],
#                          "width": masque.shape[2],
#                          "transform": out_transform})
#
#         fichier = os.path.join(dossier_output, 'masque_{}.tif'.format(suffixe))
#         liste_path.append(fichier)
#         with rasterio.open(fichier, "w", **out_meta) as dest:
#             dest.write(masque)
#
#     return liste_path
#
#
# def creation_masque(path_couche_depot, path_metrique, dossier_output):
#
#     # Création des masques des zones de dépôts et extérieur aux zones
#     with fiona.open(path_couche_depot, 'r') as shapefile:
#         polygones = [feature['geometry'] for feature in shapefile]
#
#     with rasterio.open(path_metrique) as metrique:
#         masque_ext_array, out_transform_ext = rasterio.mask.mask(metrique, polygones, crop=True)
#
#         masque_zones_array, out_transform_zones = rasterio.mask.mask(metrique, polygones, crop=False, invert=True)
#         out_meta = metrique.meta
#
#     # Enregistrement en raster dans le dossier temporaire
#     paths = enregistrement_masque(masque_ext_array, masque_zones_array, out_meta, out_transform_ext, out_transform_zones,
#                           dossier_output)
#
#     return paths
#
#
# def echantillonnage(masque_ext, masque_zone, dossier_output, path_metrique):
#
#     wbt = whitebox.WhiteboxTools()
#     wbt.verbose = False
#
#     liste_raster = [masque_ext, masque_zone]
#     liste_valeur_in = []
#     liste_valeur_out = []
#
#     # Pour chaque masque de la liste
#     for raster in liste_raster:
#
#         suffixe = ''
#         if raster == liste_raster[0]:
#             suffixe = 'in'
#         elif raster == liste_raster[1]:
#             suffixe = 'out'
#
#         # Création du raster d'échantillons aléatoire sur le masque
#         random_raster = os.path.join(dossier_output, 'random_values_{}.tif'.format(suffixe))
#         wbt.random_sample(raster, random_raster, 2000)
#
#         # Transformation du raster d'échantillon en points
#         random_point = os.path.join(dossier_output, 'random_values_{}.shp'.format(suffixe))
#         wbt.raster_to_vector_points(random_raster, random_point)
#
#         # Extraction des valeurs de la métrique à la localisation de chaque point. Les valeurs sont stockées dans
#         # un nouvel attribut de la couche
#         wbt.extract_raster_values_at_points(path_metrique, random_point, out_text=False)
#
#         # Extraction et formatage des valeurs dans un dictionnaire. La clé 'in_zone' contient la liste des valeurs
#         # à l'intérieur des zones. La clé 'out_zone' contient la liste des valeurs à l'extérieur des zones.
#         with fiona.open(os.path.join(dossier_output, 'random_values_{}.shp'.format(suffixe)), 'r') as points:
#             for feature in points:
#                 for key, value in feature.items():
#                     if key == 'properties':
#                         if raster == liste_raster[0]:
#                             liste_valeur_in.append(value['VALUE1'])
#                         elif raster == liste_raster[1]:
#                             liste_valeur_out.append(value['VALUE1'])
#
#     dict_valeurs = {'in_zone':liste_valeur_in, 'out_zone': liste_valeur_out}
#     return dict_valeurs
#
#
# def round_decade_up(n, decimals=0):
#     multiplier = 10 ** decimals
#     return math.ceil(n * multiplier) / multiplier
#
#
# def get_max_freq(dic, key):
#     max_X = None
#     max_Y = None
#
#     other_key = ''
#     if key == 'in_zone':
#         other_key = 'out_zone'
#     elif key == 'out_zone':
#         other_key = 'in_zone'
#
#     # définition de l'histogramme
#     n_1 = plt.hist(x=dic[key], bins='auto', color='#0504aa', alpha=0.7, rwidth=0.85)
#     n_2 = plt.hist(x=dic[other_key], bins='auto', color='#0504aa', alpha=0.7, rwidth=0.85)
#
#     # Valeur max en X
#     liste_max_X = [max(dic[key]), max(dic[other_key])]
#     liste_min_X = [min(dic[key]), min(dic[other_key])]
#     max_X = int(max(liste_max_X))
#     min_X = int(min(liste_min_X))
#
#     # Valeur max en Y
#     maxfreq1 = n_1[0].max()
#     maxfreq2 = n_2[0].max()
#     liste_maxfreq = [maxfreq1, maxfreq2]
#     max_Y = int(max(liste_maxfreq))
#
#     plt.cla()
#
#     return [min_X, max_X, max_Y]
#
#
# def histogramme(dic, key, metrique, feuillet, output):
#
#     maxs = get_max_freq(dic, key)
#     xmin = round(maxs[0])
#     xmax = int(round_decade_up(maxs[1], -1))
#     ymax = int(round_decade_up(maxs[2], -1))
#
#     if key == 'in_zone':
#         plt.title("{} à l'intérieur des zones de dépôts, {}".format(metrique, feuillet))
#     elif key == 'out_zone':
#         plt.title("{} à l'extérieur des zones de dépôts, {}".format(metrique, feuillet))
#
#     # définition de l'histogramme
#     n_3, bins_3, patches_3 = plt.hist(x=dic[key], bins='auto', color='#0504aa', alpha=0.7, rwidth=0.85)
#
#     # définition du min et max de l'axe des X
#     # plt.xlim((xmin, xmax))
#
#     # définition du min et max de l'axe des Y
#     plt.ylim((0, ymax))
#
#     plt.grid(axis='y', alpha=0.75)
#     plt.xlabel('Valeurs des échantillons')
#     plt.ylabel('Fréquence')
#     plt.savefig(os.path.join(output, '{}_{}_{}.png'.format(metrique, key, feuillet)))
#
#     plt.show()









#output = r'C:\Users\home\Documents\Documents\APP3\test_polygon.shp'
#raster = creation_raster(arr, path_mnt)
#polygon = conversion_polygone(dataset=mnt, output=polyg0)
# # print(polygon)
# # print(type(polygon))






