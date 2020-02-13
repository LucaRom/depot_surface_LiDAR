from osgeo import gdal
import os
import whitebox


def resampling_cubic_spline(input, output, size):

    # Création des répertoire de sortie
    head_output = os.path.dirname(output)
    if not os.path.exists(head_output):
        os.makedirs(head_output)

    # ouverture des images et extraction des dimensions
    print('Ouverture {}'.format(input))
    dataset = gdal.Open(input, gdal.GA_ReadOnly)
    largeur, hauteur = (dataset.RasterXSize, dataset.RasterYSize)

    # Resampling
    print('Resampling...')
    warp_object = gdal.WarpOptions(width=largeur / size, height=hauteur / size, resampleAlg=3)
    gdal.Warp(destNameOrDestDS=output, srcDSOrSrcDSTab=input, options=warp_object)
    print('Terminé')
    print()


def breachDepression(dem, output):

    wbt = whitebox.WhiteboxTools()
    # Création des répertoire de sortie
    head_output = os.path.dirname(output)
    if not os.path.exists(head_output):
        os.makedirs(head_output)

    # Création du MNT corrigé
    print('Creation du MNT corrigé')
    wbt.breach_depressions(dem, output)
    print('Terminé')
    print()


def relative_TPI(input, output, size):

    wbt = whitebox.WhiteboxTools()
    RUST_BACKTRACE = 1

    # Création des répertoire de sortie
    path = os.path.dirname(input)
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))

    # Répertoire de travail
    wbt.set_working_dir(path)
    wbt.verbose = False

    # Création du Relative TPI
    print('Création du TPI relatif...')
    wbt.relative_topographic_position(input, output, size, size)
    print('Terminé')
    print()


def SCA (dem, output):

    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False

    # Création du répertoire de sortie
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))

    # Création du SCA
    print('Création du SCA...')
    wbt.fd8_flow_accumulation(dem, output, out_type='specific contributing area')
    print('Terminé')
    print()


def slope(dem, output):

    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False

    # Création du répertoire de sortie
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))

    print('Création de la pente...')
    wbt.slope(dem, output)
    print('Terminé')
    print()


def TWI(slope, sca, output):

    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False

    # Création du répertoire de sortie
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))

    # Création du TWI
    print('Création du TWI...')
    wbt.wetness_index(sca, slope, output)
    print('Terminé')
    print()

