import geopandas as gpd
import random
from fiona.crs import from_epsg
from shapely.geometry import shape, Point, Polygon
from shapely.ops import nearest_points
import pandas as pd
import whitebox
import glob
from osgeo import ogr, gdal, osr
from osgeo.gdalnumeric import *
from osgeo.gdalconst import *
import os


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
        # Calcul du point le plus proche
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
    sample = gpd.GeoDataFrame(columns=['geometry', 'id', 'Zone'])
    sample.crs = from_epsg(epsg)

    # On itère dans la couche en entrée
    for ind, row in poly.iterrows():
        # Extraction de la géométrie et des limites de la couche
        geom = row['geometry']
        bbox = geom.bounds
        index = sample.sindex
        nPoints = 0
        nIterations = 0
        # Nombre d'itération maximal à faire avant d'arrêter
        maxIterations = value * 5

        random.seed()
        pointId = 0

        # Tant que le nombre d'itération maximal ou le nombre de points spécifié n'est pas atteint
        while nIterations < maxIterations and nPoints < value:

            # On génère un point aléatoire dans les limites de la couche en entrée
            height = bbox[3] - bbox[1]
            width = bbox[2] - bbox[0]
            rx = bbox[0] + width * random.random()
            ry = bbox[1] + height * random.random()

            p = Point(rx, ry)

            # On vérifie si le point est contenu dans la couche en entrée et si la distance minimale est respectée
            if p.within(geom) and (not minDistance or check_min_distance(p, minDistance, sample)):
                    # On ajoute le point à la couche de sortie
                    sample.loc[nPoints, 'geometry'] = p
                    sample.loc[nPoints, 'id'] = pointId
                    sample.loc[nPoints, 'Zone'] = zone
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

    return sample


def dissolve(geodataframe, epsg):
    '''
    :param geodataframe: Couche vectorielle à regrouper (GeoDataframe)
    :param epsg: Code EPSG à donner à l'output
    :return: Couche regroupée (GeoDataframe)
    '''
    # Si le geodataframe contient plus d'une entité
    if len(geodataframe) > 1:
        # Union de toutes les entités de la couche en 1 Multipolygon
        diss = geodataframe.unary_union
        # Création de la couche de sortie
        shpDiss = gpd.GeoDataFrame(columns=['geometry'])
        shpDiss.loc[0, 'geometry'] = diss
        shpDiss.crs = from_epsg(epsg)
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
    # Transformation en array
    arr = b1.ReadAsArray()
    # Remplacement des valeurs valides par 0
    arr[(arr >= 0)] = 0
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
    srs = ogr.osr.SpatialReference(wkt=prj)
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

    # Retrait de l'entité avec la plus petite superficie
    df = df[df['area'] != df['area'].min()]
    return df


def creation_buffer(geodataframe, distance, epsg):
    '''
    :param geodataframe: Couche à traiter (GeoDataframe)
    :param distance: Distance du buffer à créer (int)
    :param epsg: Code EPSG de la couche en sortie (int)
    :return: Couche du buffer de la couche en entrée (GeoDataframe)
    '''
    # Création de a couche de sortie
    buff = gpd.GeoDataFrame(columns=['geometry'])
    buff.crs = from_epsg(epsg)
    # Création du buffer sur la couche input et ajout du buffer dans la couche de sortie
    buff.loc[0, 'geometry'] = geodataframe.loc[0,'geometry'].buffer(distance, 16)
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
    diff.crs = from_epsg(epsg)
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

    # Lecture de la couche de dépôts et extraction du code EPSG
    print('Lecture et extraction EPSG...')
    depot = gpd.read_file(path_depot)
    epsg = int(str(depot.crs).split(':')[1])

    # Regroupement de la couche de dépôts
    print('Regroupement couche de dépôts...')
    depot_reg = dissolve(depot, epsg)

    # Multiplier le mnt par 0 pour faciliter la conversion en polygone et création du raster avec le np.array sortant
    print('Multiplication du MNT par 0...')
    path_couche_memory = "/vsimem/mnt0_poly.shp"
    mnt0_array = raster_calculation(path_mnt)
    mnt0_raster = creation_raster(mnt0_array, path_mnt)

    # Conversion du raster du mnt0 en polygone et supression des bordures pour créer le cadre d'échantillonnage
    print('Conversion MNT en polygone...')
    path_couche_memory = "/vsimem/mnt0_poly.shp"
    conversion_polygone(mnt0_raster, path_couche_memory)
    print('Suppresion des bordures...')
    cadre = delete_border(path_couche_memory)

    # Création du buffer autour de la couche de dépôts à la valeur de la distance minimale
    print('Création du buffer...')
    buff = creation_buffer(depot_reg, minDistance, epsg)

    # Clip du buffer aux dimension du cadre
    print('Clip du buffer...')
    buff_clip = gpd.clip(buff, cadre)
    #buff_clip.to_file(r'C:\Users\home\Documents\Documents\APP3\buff_clip.shp')

    # Création de la zone extérieure: différence entre le cadre et le buffer clippé
    print('Création zone externe...')
    zone_ext = difference(cadre, buff_clip, epsg)
    #zone_ext.to_file(r'C:\Users\home\Documents\Documents\APP3\difference.shp')

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
    ech_total = gpd.GeoDataFrame(pd.concat([ech_petite_zone, ech_grande_zone], ignore_index=True), crs=from_epsg(epsg))
    ech_total.to_file(output)

    # Extraction des valeurs des métriques
    print('Extraction des valeurs des métriques')
    extract_value_metrique(output, path_metriques)
    print('Terminé')


if __name__ == "__main__":

    # Chemins des couches du MNT et de la couche de dépôts
    path_depot = r'C:\Users\home\Documents\Documents\APP2\depots_31H02\zone_depots_glaciolacustre_31H02NE_MTM8_reg.shp'
    path_mnt = r'C:\Users\home\Documents\Documents\APP2\MNT_31H02NE_5x5.tif'
    path_metriques = r'C:\Users\home\Documents\Documents\APP2\Metriques\31H02\31H02NE'
    output = r'C:\Users\home\Documents\Documents\APP3\ech_total.shp'

    # Échantillonnage
    echantillonnage_pix(path_depot=path_depot, path_mnt=path_mnt, path_metriques=path_metriques,
                        output=output, nbPoints=2000, minDistance=500)



