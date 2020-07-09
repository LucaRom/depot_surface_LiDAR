import rasterio, os
from osgeo import gdal, osr
from rasterio.merge import merge
from rasterio.mask import mask
from ech_pixel import creation_buffer, creation_cadre
#import whitebox
import shutil


def resampling_cubic_spline(input, output, size):
    '''
    :param input: Chemin du raster .tif input (str)
    :param output: Chemin du fichier de sortie (str)
    :param size: Taille du rééchantillonnage (int)
    '''

    # Création des répertoire de sortie
    head_output = os.path.dirname(output)
    if not os.path.exists(head_output):
        os.makedirs(head_output)

    # ouverture des images et extraction des dimensions
    print('Ouverture {}'.format(input))
    dataset = gdal.Open(input, gdal.GA_ReadOnly)
    largeur, hauteur = (dataset.RasterXSize, dataset.RasterYSize)
    proj = dataset.GetProjection()
    crs = osr.SpatialReference()
    crs.ImportFromWkt(proj)

    # Resampling
    print('Resampling...')
    warp_object = gdal.WarpOptions(xRes=size, yRes=size, targetAlignedPixels=True, resampleAlg=3,
                                   srcSRS=crs, dstSRS=crs)
    gdal.Warp(destNameOrDestDS=output, srcDSOrSrcDSTab=input, options=warp_object)

    dataset = None
    print('Terminé')
    print()


def creation_mosaique(liste_mnt, output, epsg):
    '''
    :param liste_mnt: Liste des chemins des fichiers nécessaires pour la mosaique (list)
    :param output: Chemin du fichier de sortie (str)
    :param epsg: Code EPSG de la mosaique en sortie (int)
    :return:
    '''

    # Création d'une classe de liste pouvant être accédée par un "with"
    class liste_mosaic(list):
        def __enter__(self):
            return self
        def __exit__(self, *a):
            print('')

    # Ouverture des raster avec rasterio
    with liste_mosaic(rasterio.open(mnt) for mnt in liste_mnt) as liste_mosaic:
        # Extraction du feuillet principal
        # Création de la mosaique
        mosaique, out_trans = merge(liste_mosaic)
        # Affichage de la mosaique
        #show(mosaique, cmap='terrain')
        out_meta = liste_mosaic[0].meta.copy()
        #Update les metadata
        out_meta.update({"driver": "GTiff",
                         "height": mosaique.shape[1],
                          "width": mosaique.shape[2],
                          "transform": out_trans,
                          "crs": epsg
                          }
                        )

        # Écriture du fichier de sortie
        with rasterio.open(output, "w", **out_meta) as dest:
             dest.write(mosaique)
             dest.close()

        # Fermeture des fichiers ouverts
        for files in liste_mosaic:
            files.close()



def getFeatures(gdf):
    '''
    :param gdf: Geodataframe en entrée (Geopandas.GeoDataframe)
    :return: Les entités du gdf en json pour être utilisés par Rasterio
    '''
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]


def clip_raster_to_polygon(input_raster, input_polygon, epsg, nodata, output):
    '''
    :param input_raster: Chemin du raster .tif à clipper (str)
    :param input_polygon: Chemin de la couche polygonale .shp servant de masque pour le clip (str)
    :param epsg: Code EPSG du raster de sortie (int)
    :param nodata: Valeur NoData à attribuer au raster de sortie (int, float)
    :param output: Chemin du fichier de sortie (str)
    :return: Raster .tif clippé selon la couche polygonale en entrée
    '''

    # On ouvre la couche raster
    with rasterio.open(input_raster) as raster:
        # On parcours la couche pour en extraire les entités
        coords = getFeatures(input_polygon)
        # On clip le raster selon la couche polygonale en entrée
        out_img, out_transform = mask(dataset=raster, shapes=coords, nodata=nodata, crop=True)
        # On prend les métadonnées du raster en entrée pour le raster en sortie
        out_meta = raster.meta.copy()
        # On met à jour les métadonnées du raster en sortie avec les paramètres en intrant
        out_meta.update({"driver": "GTiff",
                         "height": out_img.shape[1],
                         "width": out_img.shape[2],
                         "transform": out_transform,
                         "nodata": nodata,
                         "crs": epsg
                         })
        # Création du fichier de sortie
        with rasterio.open(output, "w", **out_meta) as dest:
            dest.write(out_img)
            # Fermeture du fichier de sortie
            dest.close()
        # Fermeture du fichier raster en entrée
        raster.close()


def creation_buffer_raster(input_raster, input_mosaic, distance, output):
    '''
    :param input_raster: Chemin d'un fichier raster .tif de référence pour en extraire le cadre(str)
    :param input_mosaic: Chemin de la mosaique .tif à clipper (str)
    :param distance: Grosseur du buffer désirée (int)
    :param output: Chemin du fichier output, .tif de la mosaique clippée selon le raster de référence + la distance du buffer
    '''

    # Création du cadre du raster
    cadre, epsg, nodata = creation_cadre(input_raster)

    # Création du buffer autour du cadre
    buff = creation_buffer(cadre, distance, epsg, 3, 2)

    #Clip de la mosaique au buffer
    clip_raster_to_polygon(input_mosaic, buff, epsg, nodata, output)



def pretraitements(feuillet, liste_path_feuillets, distance_buffer, size_resamp, rep_output):
    '''
    :param feuillet: Numéro du feuillet sélectionné ex: 31H02NE (str)
    :param liste_path_feuillets: Liste des chemins du feuillet slectionné et de tous les feuillets adjacents pour
           la création d'un mosaique (list)
    :param distance_buffer: Grosseur du buffer à appliquer sur le raster du feuillet sélectionné (int)
    :param size_resamp: Taille du rééchantillonnage (int)
    :param rep_output: Chemin du répertoire de sortie (str)
    '''

    print('***PRÉTRAITEMENTS***')

    # Vérification des fichiers déjà présents dans le répertoire
    manquants = [path for path in liste_path_feuillets if not os.path.exists(path)]
    if len(manquants) > 0:
        print('Les fichiers suivants ne sont pas disponibles:')
        for i in manquants:
            print(i)

    # Resampling
    print('Rééchantillonnage des fichiers...')
    liste_resample = []
    for i in liste_path_feuillets:
        name = '{}_resample.tif'.format(os.path.basename(i)[:-4])
        resampled = os.path.join(rep_output, name)
        resampling_cubic_spline(i, resampled, size_resamp)
        liste_resample.append(resampled)

    # for i in liste_path_feuillets:
    #     if feuillet in i:
    #         name = '{}_resample.tif'.format(os.path.basename(i)[:-4])
    #         resampled = os.path.join(rep_output, name)
    #         resampling_cubic_spline(i, resampled, size_resamp)
    #         liste_resample.append(resampled)

    # Identification du path du feuillet et on le place en premier dans la liste pour créer la mosaique
    path_feuillet = ''
    for path in liste_resample:
        if feuillet in path:
            index_feuillet = liste_resample.index(path)
            path_feuillet = liste_resample[index_feuillet]
            first = liste_resample[0]
            liste_resample[index_feuillet] = first
            liste_resample[0] = path_feuillet

    # Identification du crs
    epsg = ''
    with rasterio.open(path_feuillet) as principal:
        epsg = principal.crs
        principal.close()
    epsg = str(epsg)

    # Création de la mosaique avec les fichiers adjacents
    print('Création de la mosaique...')
    mosaique = os.path.join(rep_output, '{}_mosaique.tif'.format(feuillet))
    creation_mosaique(liste_resample, mosaique, epsg)

    # Création du buffer autour du feuillet principal
    print('Création du buffer...')
    rep_raster_buffer = os.path.join(rep_output, feuillet[:-2])
    if not os.path.exists(rep_raster_buffer):
        os.makedirs(rep_raster_buffer)
    raster_buffer = os.path.join(rep_raster_buffer,'{}_buffer.tif'.format(feuillet))
    creation_buffer_raster(path_feuillet, mosaique, distance_buffer, raster_buffer)

    # Suppression des fichiers temporaires (mnt rééchantillonnés, mosaique)
    print('Suppression des fichiers temporaires...')
    path_backup_resamp = os.path.join(os.path.dirname(rep_output), 'resample', feuillet[:-2], 'MNT_{}_resample.tif'.format(feuillet))
    for files in liste_resample:
        if feuillet not in files:
            os.remove(files)
        else:
            if not os.path.exists(os.path.dirname(path_backup_resamp)):
                os.makedirs(os.path.dirname(path_backup_resamp))
            shutil.copy2(files, path_backup_resamp)
            os.remove(files)
    #os.remove(mosaique)

    print('Terminé')


if __name__ == '__main__':

    # Intrants
    feuillet = '31H02NE'
    liste_adj = ['31H08SO', '31H07SO', '31H07SE', '31H02SO', '31H02NO', '31H01NO', '31H01SO', '31H02NE', '31H02SE']
    #liste_adj = ['31H01SO', '31H02SO', '31H02NO', '31H02NE', '31H01NO', '31H02SE']
    #liste_adj = ['31H02SE', '31H01SO']
    #path_feuillets = r'C:\Users\home\Documents\Documents\APP2\mnt'
    path_feuillets = r'C:\Users\home\Documents\Documents\APP3\depot_surface_LiDAR\inputs\MNT\originaux'
    liste_path = []
    for root, dir, files in os.walk(path_feuillets):
        for i in liste_adj:
            liste_path.extend(os.path.join(root, j) for j in files if i in j)
    distance_buffer = 1000
    size_resamp = 5
    size_breach = 40
    rep_output = r'C:\Users\home\Documents\Documents\APP3\mnt_buffer'

    # Prétraitements
    pretraitements(feuillet=feuillet, liste_path_feuillets=liste_path, distance_buffer=distance_buffer,
                   size_resamp=size_resamp, rep_output=rep_output)
