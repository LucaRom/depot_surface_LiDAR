import geopandas as gpd
import random
from fiona.crs import from_epsg
from shapely.geometry import shape, Point, Polygon
from shapely.ops import nearest_points
import matplotlib.pyplot as plt
import descartes


path = r'C:\Users\home\Documents\Documents\APP2\polygon_test.shp'
#path = r'C:\Users\home\Documents\Documents\APP2\depots_31H02\zone_depots_glaciolacustre_31H02NE_MTM8_reg.shp'
value = 2000
minDistance = 500


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

## DISSOLVE ##

def dissolve(geodataframe):
    diss = geodataframe.unary_union
    shpDiss = gpd.GeoDataFrame(columns=['geometry'])
    shpDiss.loc[0, 'geometry'] = diss
    return shpDiss

## RASTER CALCULATION ##

def raster_calculation(path_raster):
    mnt = gdal.Open(path_raster)
    b1 = mnt.GetRasterBand(1)
    arr = b1.ReadAsArray()
    arr[(arr >= 0)] = 0
    return arr

def creation_raster (inputArray,inputMet):
    # On crée une image GEOTIFF en sortie
    # je déclare tous les drivers
    gdal.AllRegister()
    # le driver que je veux utiliser GEOTIFF
    driver = gdal.GetDriverByName("MEM")

    # taille de mon image (ce sera la taille de la matrice)
    rows, cols = inputArray.shape

    # je déclare mon image
    # il faut : la taille, le nombre de bandes et le type de données (ce sera des bytes)
    image = driver.Create('MEM',cols, rows, 1, GDT_Float64)

    # J'extrais les paramètres d'une métriques pour le positionnement du fichier sortant
    data = gdal.Open(inputMet)

    # J'applique les paramètres de positionnement
    geoTransform = data.GetGeoTransform()
    data = None # On vide la mémoire

    # On donne la coordonnée d'origine de l'image raster tiré d'une des métriques
    image.SetGeoTransform(geoTransform)

    # je cherche la bande 1
    band = image.GetRasterBand(1)

    # Je remets la matrice en 2 dimension
    # result1 = resultat.reshape(resultat.shape[1], resultat.shape[2])
    #result1 = inputArray.reshape(inputArray.shape[0], inputArray.shape[1])

    # j'écris la matrice dans la bande
    # band.WriteArray(result1, 0, 0)
    band.WriteArray(inputArray, 0, 0)

    # Je définis la projection
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(2950)

    image.SetProjection(outRasterSRS.ExportToWkt())

    # je vide la cache
    band.FlushCache()
    band.SetNoDataValue(-99)

    return image


def conversion_polygone (dataset, output):
    gdal.UseExceptions()
    type_mapping = {gdal.GDT_Byte: ogr.OFTInteger,
                    gdal.GDT_UInt16: ogr.OFTInteger,
                    gdal.GDT_Int16: ogr.OFTInteger,
                    gdal.GDT_UInt32: ogr.OFTInteger,
                    gdal.GDT_Int32: ogr.OFTInteger,
                    gdal.GDT_Float32: ogr.OFTReal,
                    gdal.GDT_Float64: ogr.OFTReal,
                    gdal.GDT_CInt16: ogr.OFTInteger,
                    gdal.GDT_CInt32: ogr.OFTInteger,
                    gdal.GDT_CFloat32: ogr.OFTReal,
                    gdal.GDT_CFloat64: ogr.OFTReal}

    srcband = dataset.GetRasterBand(1)
    maskband = dataset.GetRasterBand(2)
    prj = dataset.GetProjection()
    dst_layername = os.path.join("/vsimem/" + output + '.shp')
    drv = ogr.GetDriverByName('ESRI Shapefile')
    dst_ds = drv.CreateDataSource(dst_layername)
    srs = ogr.osr.SpatialReference(wkt=prj)
    dst_layer = dst_ds.CreateLayer(dst_layername, srs=srs)
    raster_field = ogr.FieldDefn('id', type_mapping[srcband.DataType])
    gdal.Polygonize(srcband, None, dst_layer, -1, [], callback=None)
    return dst_layer


def delete_border(path_shp):
    df = gpd.read_file(path_shp)
    df['area'] = [i.area for i in df['geometry']]
    df = df[df['area'] != df['area'].min()]
    df.to_file(polyg0)
    return df


from osgeo import ogr, gdal, osr
from osgeo.gdalnumeric import *
from osgeo.gdalconst import *
import os

path_mnt = r'C:\Users\home\Documents\Documents\APP2\MNT_31H02NE_5x5.tif'
path_mnt0 = r'C:\Users\home\Documents\Documents\APP3\test_mnt0.tif'
polyg0 = r'C:\Users\home\Documents\Documents\APP3\test_mnt0_poly.shp'



raster = creation_raster(arr, path_mnt)
pol = conversion_polygone(dataset=raster, output='mnt0')











#output = r'C:\Users\home\Documents\Documents\APP3\test_polygon.shp'
#raster = creation_raster(arr, path_mnt)
#polygon = conversion_polygone(dataset=mnt, output=polyg0)
# # print(polygon)
# # print(type(polygon))






