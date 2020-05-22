import rasterio, os
from osgeo import gdal, osr
from rasterio.merge import merge
from ech_pixel import raster_calculation, creation_raster, creation_buffer, conversion_polygone, delete_border


def resampling_cubic_spline(input, output, size):

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
    warp_object = gdal.WarpOptions(width=largeur / size, height=hauteur / size,
                                   resampleAlg=3, srcSRS=crs, dstSRS=crs)
    gdal.Warp(destNameOrDestDS=output, srcDSOrSrcDSTab=input, options=warp_object)

    dataset = None
    print('Terminé')
    print()


def creation_mosaique(liste_mnt, output, epsg):

    # Création d'une classe de liste pouvant être accédée par un "with"
    class liste_mosaic(list):
        def __enter__(self):
            return self
        def __exit__(self, *a):
            print('')

    # Ouverture des raster avec rasterio
    with liste_mosaic(rasterio.open(mnt) for mnt in liste_mnt) as liste_mosaic:
        # Création de la mosaique
        mosaique, out_trans = merge(liste_mosaic)
        # Affichage de la mosaique
        #show(mosaique, cmap='terrain')
        out_meta = liste_mosaic[0].meta.copy()
        # Update les metadata
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


def creation_buffer_raster(input_raster, input_mosaic, distance, output, epsg):

    # Transormation du MNT en en valeurs 0 pour simplifier la polygonisation
    mnt0 = raster_calculation(input_raster)

    # Création d'un raster en mémoire
    mnt0_raster = creation_raster(mnt0, input_raster)

    # Conversion en polygone dans un couche en mémoire et suppression des bordures
    path_couche_memory = "/vsimem/mnt0_poly.shp"
    mnt0_poly = conversion_polygone(mnt0_raster, path_couche_memory)
    cadre = delete_border(path_couche_memory)

    # Création du buffer autour du cadre
    buff = creation_buffer(cadre, distance, epsg, 3, 2)
    path_buff = "/vsimem/buffer.shp"
    buff.to_file(path_buff)

    # Clip de la mosaique au buffer
    clip = gdal.Warp(output, input_mosaic, cutlineDSName=path_buff)


def pretraitements(feuillet, liste_path_feuillets, distance_buffer, size_resamp, rep_output):

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

    # Identification du path du feuillet et de son crs
    path_feuillet = ''
    for path in liste_resample:
        if feuillet in path:
            path_feuillet = path

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
    raster_buffer = os.path.join(rep_output, '{}_buffer.tif'.format(feuillet))
    creation_buffer_raster(path_feuillet, mosaique, distance_buffer, raster_buffer, epsg)

    # Suppression des fichiers temporaires (mnt rééchantillonnés, mosaique)
    print('Suppression des fichiers temporaires...')
    for files in liste_resample:
        os.remove(files)
    os.remove(mosaique)

    print('Terminé')


if __name__ == '__main__':

    # Intrants
    feuillet = '31H02NE'
    liste_adj = ['31H08SO', '31H07SO', '31H07SE', '31H02SO', '31H02NO', '31H01NO', '31H01SO', '31H02NE', '31H02SE']
    path_feuillets = r'C:\Users\home\Documents\Documents\APP2\mnt'
    liste_path = []
    for root, dir, files in os.walk(path_feuillets):
        for i in liste_adj:
            liste_path.extend(os.path.join(root, j) for j in files if i in j)
    distance_buffer = 1000
    size_resamp = 50
    rep_output = r'C:\Users\home\Documents\Documents\APP2\mnt_buffer'

    # Prétraitements
    pretraitements(feuillet=feuillet, liste_path_feuillets=liste_path, distance_buffer=distance_buffer,
                   size_resamp=size_resamp, rep_output=rep_output)
