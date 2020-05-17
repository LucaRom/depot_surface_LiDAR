# import geopandas as gpd
# import random
# from fiona.crs import from_epsg
# from shapely.geometry import shape, Point, Polygon
# from shapely.ops import nearest_points
# import pandas as pd
# import whitebox
# import glob
# from osgeo import ogr, gdal, osr
# from osgeo.gdalnumeric import *
# from osgeo.gdalconst import *
# import os



## GLCM DE R###

import subprocess

path_r = r"C:\Program Files\R\R-3.6.3\bin\Rscript.exe"
path_script = r"C:\Users\home\Documents\Documents\APP2\haralick.R"
input = r"C:\Users\home\Documents\Documents\APP2\Metriques50m\31H02\31H02NE\Pente_WB_31H02NE_50m.tif"
output = r"C:\Users\home\Documents\Documents\APP2\haralick\testR.tif"
texture = "1"
kernel = "3"

command = [path_r, path_script, input, output, texture, kernel]


def tetures_glcm(path_r, path_script, input, output, texture, kernel):
    '''
    Nécessite l'installation de R 3.6 et +.
    :param path_r: Chemin vers l'application Rscript.exe (str)
    :param path_script: Chemin vers le script 'haralick.R' (str)
    :param input: Chemin du MNT à traiter (str)
    :param output: Chemin du fichier de sortie (str)
    :param texture: Texture d'haralick à créer (str)
                    - 1 => moyenne
                    - 2 => correlation
                    - 3 => contraste
    :param kernel: Taille du Kernel (str)
    :return: Raster de la métrique d'haralick voulue sur le MNT en entrée (.tif)
    '''
    # On crée la liste de commande à passer
    commande = [path_r, path_script, input, output, texture, kernel]
    run_command(commande)


def run_command(command):
    '''
    Source:  Kannan Ponnusamy (2015), https://www.endpoint.com/blog/2015/01/28/getting-realtime-output-using-python
    :param command: Liste de commandes à passer dans le terminal (list)
    :return: Affiche les output de la console en temps réel tant que le processus n'est pas fini (process.poll() est None)
    '''
    # On passe la commande dans le terminal
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    while True:
        # On itère dans le output tant que le code de sortie est None. Si une nouvelle ligne apparaît, on l'affiche
        output = process.stdout.readline()
        if output == b'' and process.poll() is not None:
            # Si le processus se termine, on quitte la boucle
            break
        if output:
            print(output.strip())
    ExitCode = process.poll()
    return ExitCode


run_command(command)

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











#output = r'C:\Users\home\Documents\Documents\APP3\test_polygon.shp'
#raster = creation_raster(arr, path_mnt)
#polygon = conversion_polygone(dataset=mnt, output=polyg0)
# # print(polygon)
# # print(type(polygon))






