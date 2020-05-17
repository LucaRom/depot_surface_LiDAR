from osgeo import gdal, osr
import os
import whitebox
import subprocess


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


def textures_glcm(path_r, path_script, input, output, metrique, kernel):
    '''
    Nécessite l'installation de R 3.6 et +.
    :param path_r: Chemin vers l'application Rscript.exe (str)
    :param path_script: Chemin vers le script 'haralick.R' (str)
    :param input: Chemin du MNT à traiter (str)
    :param output: Chemin du fichier de sortie (str)
    :param metrique: metrique d'haralick à créer (str)
                    - 1 => moyenne
                    - 2 => correlation
                    - 3 => contraste
    :param kernel: Taille du Kernel (str)
    :return: Raster de la métrique d'haralick voulue sur le MNT en entrée (.tif)
    '''
    # On crée la liste de commande à passer
    commande = [path_r, path_script, input, output, metrique, kernel]
    # On passe la liste de commande dans le terminal
    run_command(commande)


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
    warp_object = gdal.WarpOptions(width=largeur / size, height=hauteur / size, resampleAlg=3, srcSRS=crs, dstSRS=crs)
    gdal.Warp(destNameOrDestDS=output, srcDSOrSrcDSTab=input, options=warp_object)
    print('Terminé')
    print()



def breachDepression(dem, output):

    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False

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


def fpdems(dem, output):

    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False

    # Création du répertoire de sortie
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))

    # Filtrage
    print('Filtrage du mnt...')
    wbt.feature_preserving_smoothing(dem, output)
    print('Terminé')
    print()


def gdal_translate_32to64(input, output):

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
    translate_object = gdal.TranslateOptions(width=largeur, height=hauteur, outputType=gdal.GDT_Float64)
    gdal.Translate(destName=output, srcDS=input, options=translate_object)
    print('Terminé')
    print()


def CircularVarofAspect(dem, output, size):

    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False

    # Création du répertoire de sortie
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))

    # Création du CircularVarianceOfAspect
    print('Creation du CircularVarianceOfAspect...')
    wbt.circular_variance_of_aspect(dem, output, size)
    print('Terminé')
    print()


def EdgeDensity(dem, output, size, seuil):

    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False

    # Création du répertoire de sortie
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))

    # Création du Edge Density
    print('Creation du EdgeDensity...')
    wbt.edge_density(dem, output, size, seuil)
    print('Terminé')
    print()


def sphericalStdDevNormals(dem, output, size):

    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False

    # Création du répertoire de sortie
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))

    # Création du Spherical Standard Deviation of Normals
    print('Creation du Spherical Standard Deviation of Normals...')
    wbt.spherical_std_dev_of_normals(dem, output, size)
    print('Terminé')
    print()


def plan_curvature(dem, output):

    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False

    # Création du répertoire de sortie
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))

    # Création du plan curvature
    print('Creation du plan curvature...')
    wbt.plan_curvature(dem, output)
    print('Terminé')
    print()


def profile_curvature(dem, output):

    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False

    # Création du répertoire de sortie
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))

    # Création du profile curvature
    print('Creation du profile curvature...')
    wbt.profile_curvature(dem, output)
    print('Terminé')
    print()


def tan_curvature(dem, output):

    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False

    # Création du répertoire de sortie
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))

    # Création du tan curvature
    print('Creation du tan curvature...')
    wbt.tangential_curvature(dem, output)
    print('Terminé')
    print()


def Downslope_Ind(dem, output):

    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False

    # Création du répertoire de sortie
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))

    # Création du Downslope Index
    print('Creation du Downslope Index...')
    wbt.downslope_index(dem, output)
    print('Terminé')
    print()


def AverNormVectAngDev(dem, output, size):

    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False

    # Création du répertoire de sortie
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))

    # Average Normal Vector Angular Deviation
    print('Creation du Average Normal Vector Angular Deviation ...')
    wbt.average_normal_vector_angular_deviation(dem, output, size)
    print('Terminé')
    print()