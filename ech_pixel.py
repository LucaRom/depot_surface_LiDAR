import geopandas as gpd
import random
#from fiona.crs import from_epsg
from shapely.geometry import Point, box, Polygon, MultiPolygon, GeometryCollection
from shapely.ops import nearest_points
import pandas as pd
import whitebox
import glob
from osgeo import ogr, gdal, osr
from osgeo.gdalnumeric import *
#from osgeo.gdalconst import *
import os
#import rtree
#import numpy as np



def katana(geometry, threshold, count=0):

    """Split a Polygon into two parts across it's shortest dimension
    Copyright (c) 2016, Joshua Arnott
    url: https://snorfalorpagus.net/blog/2016/03/13/splitting-large-polygons-for-faster-intersections/"""

    bounds = geometry.bounds
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    if max(width, height) <= threshold or count == 250:
        # either the polygon is smaller than the threshold, or the maximum
        # number of recursions has been reached
        return [geometry]
    if height >= width:
        # split left to right
        a = box(bounds[0], bounds[1], bounds[2], bounds[1]+height/2)
        b = box(bounds[0], bounds[1]+height/2, bounds[2], bounds[3])
    else:
        # split top to bottom
        a = box(bounds[0], bounds[1], bounds[0]+width/2, bounds[3])
        b = box(bounds[0]+width/2, bounds[1], bounds[2], bounds[3])
    result = []
    for d in (a, b,):
        c = geometry.intersection(d)
        if not isinstance(c, GeometryCollection):
            c = [c]
        for e in c:
            if isinstance(e, (Polygon, MultiPolygon)):
                result.extend(katana(e, threshold, count+1))
    if count > 0:
        return result
    # convert multipart into singlepart
    final_result = []
    for g in result:
        if isinstance(g, MultiPolygon):
            final_result.extend(g)
        else:
            final_result.append(g)

    return final_result


def check_min_distance(point, distance, points):
    '''
    :param point: Géométrie à comparer avec la couche Points (shapely.Point)
    :param distance: Distance minimale à respecter (int)
    :param points: Couche de points à comparer avec la géométrie point (GeoDataframe)
    :return: vrai si la distance entre le point et la couche de points est inférieure à la distance minimale
    '''
    if distance == 0:
        return True
    if len(points) > 0:
        # Union de toutes les géométries de la couche points en multipoint
        uni = points.unary_union
        # # Calcul du point le plus proche
        nearest = nearest_points(point, uni)
        # Comparaison de la distance du point le plus proche à la distance minimale
        if len(nearest) == 0:
            return True
        if nearest[1].distance(point) < distance:
            return False
    return True


def echantillon_pixel(poly, minDistance, value, epsg, zone):
    '''
    Inspiré du script : RandomPointsPolygons.py disponible dans QGIS 3.10
    ---------------------
    Date                 : April 2014
    Copyright            : (C) 2014 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com

    :param poly: de la couche polygonale à échantillonner (GeoDataframe)
    :param minDistance: Distance minimale à respecter entre les points (int)
    :param value: Nombre de points désirés (int)
    :param epsg: Code EPSG à attribuer à la couche sortante (int)
    :param zone: Attribut zone ajouté à chaque points échantillonnés (char)
    :return: Un GeoDataframe des points échantillonnés
    '''

    # Création de la couche de sortie
    #poly = gpd.read_file(input)
    sample = gpd.GeoDataFrame(columns=['geometry'])
    sample.crs = epsg

    # On itère dans la couche en entrée
    for ind, row in poly.iterrows():
        # Extraction de la géométrie et des limites de la couche
        geom = row['geometry']
        bbox = geom.bounds
        height = bbox[3] - bbox[1]
        width = bbox[2] - bbox[0]

        # Subdivision du polygone en plus petits
        liste_subPoly = katana(geom, 1000)
        subPoly = gpd.GeoDataFrame()
        subPoly.crs = epsg
        subPoly['geometry'] = liste_subPoly

        # On crée un index spatial sur la couche des subdivision
        indexSub = subPoly.sindex

        nPoints = 0
        nIterations = 0
        # Nombre d'itération maximal à faire avant d'arrêter
        maxIterations = value * 200

        random.seed()
        pointId = 0
        #liste_points = []

        # Tant que le nombre d'itération maximal ou le nombre de points spécifié n'est pas atteint
        while nIterations < maxIterations and nPoints < value:

            # On génère un point aléatoire dans les limites de la couche en entrée
            rx = bbox[0] + width * random.random()
            ry = bbox[1] + height * random.random()

            p = Point(rx, ry)

            # On fait la liste des index qui qui touche au point
            intersect_possible = list(indexSub.intersection(p.bounds))
            if len(intersect_possible) > 0:

                # On extrait le polygone correspondant dans la couche des subdivisions
                polyCorresp = subPoly.iloc[intersect_possible]['geometry'].values[0]

                # On vérifie si le point est contenu dans le polygone et si la distance minimale est respectée
                if p.within(polyCorresp) and (not minDistance or check_min_distance(p, minDistance, sample)):
                    # On ajoute le point à la liste de sortie
                    # liste_points.append(p)

                    # On ajoute le point dans le dataframe sortant
                    sample.loc[pointId, 'geometry'] = p
                    nPoints += 1
                    pointId += 1

            # On incrémente le nombre d'itération
            nIterations += 1
            if nIterations % 1000 == 0:
                print(nIterations)

        # On spécifie si le nombre maximal d'iétration a été atteint avant le nombre de point voulu
        if nPoints < value:
            print(sample)
            print("Le nombre de points voulu n'a pas pu être généré. Nombre maximal d'itération atteint")

        # Rajout de l'identifiant de la zone
        sample['Zone'] = zone
    return sample


def dissolve(geodataframe):
    '''
    :param geodataframe: Couche vectorielle à regrouper (GeoDataframe)
    :param epsg: Code EPSG à donner à l'output
    :return: Couche regroupée (GeoDataframe)
    '''
    # Si le geodataframe contient plus d'une entité
    if len(geodataframe) > 1:
        epsg = geodataframe.crs
        # Union de toutes les entités de la couche en 1 Multipolygon
        diss = geodataframe.unary_union
        # Création de la couche de sortie
        shpDiss = gpd.GeoDataFrame(columns=['geometry'])
        shpDiss.loc[0, 'geometry'] = diss
        shpDiss.crs = epsg
        return shpDiss
    # Si le geodataframe ne contient qu'une entité, retourne le geodataframe en input
    return geodataframe


def raster_calculation(path_raster):
    '''
    :param path_raster: Chemin du raster à traiter (str)
    :return: Array du raster avec les valeurs valides à 0 (np.darray)
    '''
    # Lecture du raster
    mnt = gdal.Open(path_raster)
    b1 = mnt.GetRasterBand(1)
    nodata = b1.GetNoDataValue()
    # Transformation en array
    arr = b1.ReadAsArray()
    # Remplacement des valeurs valides par 0
    arr[(arr != nodata)] = 0
    return arr


def creation_raster (inputArray,inputMet):
    '''
    :param inputArray: Array à transformer en Raster (np.array)
    :param inputMet: Chemin du Raster de référence pour les dimensions et le CRS (str)
    :return: Raster géoréférencé de l'array en entrée. La sauvegarde est effectuée en mémoire (gdal.dataset)
    '''
    # On crée une image GEOTIFF en sortie
    # je déclare tous les drivers
    gdal.AllRegister()
    # le driver que je veux utiliser GEOTIFF
    driver = gdal.GetDriverByName("MEM")

    # taille de mon image (ce sera la taille de la matrice)
    rows, cols = inputArray.shape

    # je déclare mon image
    # il faut : la taille, le nombre de bandes et le type de données (ce sera des bytes)
    image = driver.Create('MEM',cols, rows, 1, gdal.GDT_Float64)

    # J'extrais les paramètres d'une métriques pour le positionnement du fichier sortant
    data = gdal.Open(inputMet)
    geoTransform = data.GetGeoTransform()
    proj = data.GetProjection()
    nodata = data.GetRasterBand(1).GetNoDataValue()
    data = None # On vide la mémoire

    # j'écris la matrice dans la bande
    image.GetRasterBand(1).WriteArray(inputArray, 0, 0)

    # On donne les paramètres de l'image raster tiré d'une des métriques
    image.SetGeoTransform(geoTransform)
    image.SetProjection(proj)
    image.GetRasterBand(1).SetNoDataValue(nodata)

    # je vide la cache
    image.FlushCache()

    return image, proj, nodata


def conversion_polygone (dataset, output):
    '''
    :param dataset: Dataset à convertir en polygone (gdal.dataset)
    :param output: Chemin de sauvegarde (str)
    :return: Couche polygonale (driver ESRI Shapefile)
    '''
    gdal.UseExceptions()

    # Format possibles de données
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

    # Création du fichier de sortie
    srcband = dataset.GetRasterBand(1)
    prj = dataset.GetProjection()
    dst_layername = os.path.join(output)
    drv = ogr.GetDriverByName('ESRI Shapefile')
    dst_ds = drv.CreateDataSource(dst_layername)
    srs = osr.SpatialReference(wkt=prj)
    dst_layer = dst_ds.CreateLayer(dst_layername, srs=srs)
    raster_field = ogr.FieldDefn('id', type_mapping[srcband.DataType])

    # Conversion en polygone vers le fichier de sortie
    gdal.Polygonize(srcband, None, dst_layer, -1, [], callback=None)


def delete_border(path_shp):
    '''
    :param path_shp: Chemin d'une couche polygonale avec des bordures à retirer. (output de conversion_polygone) (str)
    :return: Couche polygonale sans bordures (GeoDataframe)
    '''
    # Lecture en GeoDataframe
    df = gpd.read_file(path_shp)
    df['area'] = [i.area for i in df['geometry']]

    # Création gdf de sortie
    output = gpd.GeoDataFrame(columns=['geometry'])

    # On garde seulement la plus grande entité et on l'ajoute au gdf de sortie
    max = df[df['area'] == df['area'].max()]['geometry'].values[0]
    output.loc[0, 'geometry'] = max

    return output


def creation_buffer(geodataframe, distance, epsg, cap_style, join_style):
    '''
    :param geodataframe: Couche à traiter (GeoDataframe)
    :param distance: Distance du buffer à créer (int)
    :param epsg: Code EPSG de la couche en sortie (int)
    :return: Couche du buffer de la couche en entrée (GeoDataframe)
    '''
    # Création de a couche de sortie
    buff = gpd.GeoDataFrame(columns=['geometry'])
    buff.crs = epsg
    # Création du buffer sur la couche input et ajout du buffer dans la couche de sortie
    buff['geometry'] = geodataframe['geometry'].buffer(distance, cap_style=cap_style, join_style=join_style)
    return buff


def difference(input, mask, epsg):
    '''
    :param input: Couche source, une entité (GeoDataframe)
    :param mask: Couche de masque, une entité (GeoDataframe)
    :param epsg: Code EPSG de la couche en sortie
    :return: Couche de la différence entre input et mask (GeoDataframe)
    '''
    # Extraction des géométries à différencier
    source = input.loc[0, 'geometry']
    masque = mask.loc[0, 'geometry']
    # Création de la couche de sortie
    diff = gpd.GeoDataFrame(columns=['geometry'])
    diff.crs = epsg
    # Calcul de la différence et ajout de la différence à la couche de sortie
    diff.loc[0, 'geometry'] = source.difference(masque)
    return diff


def comparaison_area(gdf1, gdf2):
    '''
    :param gdf1: Couche 1, une entité (GeoDataframe)
    :param gdf2: Couche 2, une entité (GeoDataframe)
    :return: Vrai si l'aire de l'entité de la couche 1 est inférieure à celle
    de l'entité de la couche 2. Faux si c'est l'inverse
    '''
    # Calcul de l'aire de l'entité des 2 couches
    area1 = gdf1.loc[0, 'geometry'].area
    area2 = gdf2.loc[0, 'geometry'].area
    # Comparaison
    if area1 < area2:
        return True
    else:
        return False


def extract_value_metrique(path_couche_point, path_metrique):
    '''
    :param path_couche_point: Chemin de la couche de point. Les valeurs seront extraites dans les points (str)
    :param path_metrique: Chemin du répertoire contenant la/les images dont il faut extraire les valeur (str)
    :return: Couche points en input, contenant les valeurs des images pour chaque points (.shp)
    '''

    wbt = whitebox.WhiteboxTools()
    # Lecture des métriques
    print('lecture des métriques...')
    ls = glob.glob(path_metrique + os.sep + '*.tif')
    dic_ordre = {}

    # Préparation de la chaîne de métrique à mettre en input dans la fonction d'extraction
    print('préparation de la chaine de métriques...')
    chaine_metrique=''
    for i in range(len(ls)):
        metrique = ls[i]
        nom = os.path.basename(metrique).split('_')[0]
        #name = dic_metrique[nom_basename]
        dic_ordre.update({str(i+1):nom})

        if chaine_metrique == '':
            chaine_metrique = metrique
        else:
            chaine_metrique = chaine_metrique + ';' + metrique
    print(dic_ordre)

    # Extraction des valeurs des images du répertoire selon l'odre de la chaîne. Les valeurs sont ajoutée dans la couche
    print('Extraction des valeurs...')
    wbt.extract_raster_values_at_points(chaine_metrique, points=path_couche_point)

    # Lecture de la couche de point résultante
    print('Ouverture du SHP...')
    shp = gpd.read_file(path_couche_point)
    # del shp['VALUE']

    # Changement du nom des colonnes 'VALUE' pour le vrai nom des images
    print('Création des nouvelles colonnes...')
    for col in shp.columns:
        if col == 'id' or col == 'geometry':
            pass
        elif col[0:5] == 'VALUE':
            num = col[5:]
            nom_colonne = dic_ordre[num]
            shp[nom_colonne] = shp[col].round(4)

    print('Suppression des anciennes colonnes...')
    for col in shp.columns:
        if col[0:5] == 'VALUE':
            del shp[col]

    # Sauvegarde de la couche résultante au même endroit
    print('Sauvegarde...')
    shp.to_file(path_couche_point)

def creation_cadre(input_raster):
    '''
    :param input_raster: Path raster dont on veut extraire le cadre (str)
    :return: geodataframe de la couche du cadre du raster en entrée (Geopandas.GeoDataframe())
    '''
    # Multiplier le mnt par 0 pour faciliter la conversion en polygone et création du raster avec le np.array sortant
    print('Multiplication du MNT par 0...')
    ras0_array = raster_calculation(input_raster)
    ras0_raster, proj, nodata = creation_raster(ras0_array, input_raster)

    # Extraction su code EPSG de la métrique
    epsg = 'epsg:{}'.format(osr.SpatialReference(wkt=proj).GetAttrValue('AUTHORITY', 1))

    # Conversion du raster du mnt0 en polygone et supression des bordures pour créer le cadre d'échantillonnage
    print('Conversion MNT en polygone...')
    path_couche_memory = "/vsimem/ras0_poly.shp"
    conversion_polygone(ras0_raster, path_couche_memory)
    print('Suppresion des bordures...')
    cadre = delete_border(path_couche_memory)
    return cadre, epsg, nodata


def echantillonnage_pix(path_depot, path_mnt, path_metriques, output, nbPoints, minDistance):
    '''
    :param path_depot: Chemin de la couche de dépôts (str)
    :param path_mnt: Chemin du MNT à échantillonner (str)
    :param path_metriques: Chemin du répertoire contenant les métriques à échantillonner (str)
    :param output: Chemin du fichier de sortie (str)
    :param nbPoints: Nombre de points voulus (int)
    :param minDistance: Distance minimale à respecter entre les points (int)
    :return: Couche de points échantillonnés aléatoirement sur le MNT avec les valeurs des métriques comme attribut (shp)
    '''

    print('***ÉCHANTILLONNAGE PAR PIXEL***')

    # Création du cadre du MNT
    print('Création du cadre...')
    cadre, epsg, nodata = creation_cadre(path_mnt)

    # Lecture de la couche de dépôts et reprojection si nécessaire
    print('Lecture de la couche de dépôts...')
    depot = gpd.read_file(path_depot)

    if str(depot.crs) != epsg:
        print('Reprojection...')
        depot.crs = epsg

    # Regroupement de la couche de dépôts
    print('Regroupement couche de dépôts...')
    depot_reg = dissolve(depot)

    # Création du buffer autour de la couche de dépôts à la valeur de la distance minimale
    print('Création du buffer...')
    buff = creation_buffer(depot_reg, minDistance, epsg, 1, 1)

    # # Clip du buffer aux dimension du cadre
    print('Clip du buffer...')
    buff_clip = gpd.clip(buff, cadre)

    # Création de la zone extérieure: différence entre le cadre et le buffer clippé
    print('Création zone externe...')
    zone_ext = difference(cadre, buff_clip, epsg)

    # Comparaison de superficie entre les dépôts et la zone extérieure pour fixer la limite du nombre de points
    print('Comparaison...')
    plus_petite_zone = None
    plus_grande_zone = None
    zone = None
    if comparaison_area(depot_reg, zone_ext):
        plus_petite_zone = depot_reg
        plus_grande_zone = zone_ext
        zone = 1
        print('Plus petite zone: couche de dépôts ')
    else:
        plus_petite_zone = zone_ext
        plus_grande_zone = depot_reg
        zone = 0
        print('Plus petite zone: zone extérieure')

    # Échantillonnage de la plus petite zone
    print('Échantillonnage petite zone...')
    ech_petite_zone = echantillon_pixel(plus_petite_zone, minDistance, nbPoints, epsg, zone)
    #ech_petite_zone.to_file(r'C:\Users\home\Documents\Documents\APP3\ech_petite_zone.shp')

    # Échantillonnage de la plus grande zone selon le nombre de points contenu dans la petite zone
    if zone == 1:
        zone = 0
    elif zone == 0:
        zone = 1
    print('Échantillonnage grande zone...')
    nbPoints_petite = len(ech_petite_zone)
    ech_grande_zone = echantillon_pixel(plus_grande_zone, minDistance, nbPoints_petite, epsg, zone)
    #ech_grande_zone.to_file(r'C:\Users\home\Documents\Documents\APP3\ech_grande_zone.shp')
    print('Terminé')

    # Combinaison des deux zones
    print('Combinaison des échantillons...')
    ech_total = gpd.GeoDataFrame(pd.concat([ech_petite_zone, ech_grande_zone], ignore_index=True), crs=epsg)
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))
    ech_total.to_file(output)

    # Extraction des valeurs des métriques
    print('Extraction des valeurs des métriques')
    extract_value_metrique(output, path_metriques)
    print('Terminé')


if __name__ == "__main__":

    # Chemins des couches du MNT et de la couche de dépôts
    path_depot = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\inputs\depots\31H02NE\zones_depots_glaciolacustres_31H02NE.shp'
    path_mnt = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\Backup\MNT_31H02NE_resample.tif'
    path_metriques = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\inputs\tiffs\31H02NE'
    output = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\inputs\ech_entrainement_mod\pixel\31H02_no_anth\ech_31H02NE.shp'
    path_zone_dev = r'C:\Users\home\Documents\Documents\APP2\depot_surface_LiDAR\inputs\zone_developpees\31H02\zone_dev_31H02NE.shp'

    import time

    start = time.time()
    # Échantillonnage
    echantillonnage_pix(path_depot=path_depot, path_mnt=path_mnt, path_metriques=path_metriques,
                        output=output, nbPoints=2000, minDistance=500)
    # path_zone = r'C:\Users\home\Documents\Documents\APP3\difference.shp'
    # zone = gpd.read_file(path_zone)
    # ech_diff = echantillon_pixel(poly=zone, minDistance=500, value=143, epsg='EPSG:2145', zone=0)
    # ech_diff.to_file(r'C:\Users\home\Documents\Documents\APP3\eff_diff.shp')
    end = time.time()
    print(end-start)


