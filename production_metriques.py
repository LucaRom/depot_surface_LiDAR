from fonctions_metriques import *
import os


def creation_metriques(mnt, feuillet, rep_output, path_r, path_script):

    print('***CRÉATION DES MÉTRIQUES***')

    # répertoire temporaire
    temp = os.path.join(rep_output, 'temp')

    # # Extraction du nom du feuillet
    # feuillet = os.path.basename(mnt).split('_')[0]

    # # Repertoire de sortie des metrique
    # dir_metrique =os.path.join(rep_output, division_feuillet)

    # Création du TPI relatif avec un kernel de 200m
    TPI = os.path.join(rep_output, 'TPI_WB_{}.tif'.format(feuillet))
    relative_TPI(mnt, TPI, 40)

    # Correction hydrologique, breach depressions pour le calcul du SCA
    MNTBreachDepression = os.path.join(temp, 'MNT_BD_{}.tif'.format(feuillet))
    breachDepression(mnt, MNTBreachDepression)

    # Création du SCA
    sca = os.path.join(temp, 'SCA_{}.tif'.format(feuillet))
    SCA(MNTBreachDepression, sca)

    # Création de la pente
    pente = os.path.join(rep_output, 'Pen_WB_{}.tif'.format(feuillet))
    slope(mnt, pente)

    # Creation du TWI
    twi = os.path.join(rep_output, 'TWI_WB_{}.tif'.format(feuillet))
    TWI(pente, sca, twi)

    ## Creation du profile Curvature
    profCur = os.path.join(rep_output, 'PC_WB_{}.tif'.format(feuillet))
    profile_curvature(mnt, profCur)

    ## Creation du Circular Variance of Aspect
    cirVar = os.path.join(rep_output, 'CVA_WB_{}.tif'.format(feuillet))
    CircularVarofAspect(mnt, cirVar, 39)

    ## Création du Spherical Std Deviation of Normals
    sphStd = os.path.join(rep_output, 'SSDN_WB_{}.tif'.format(feuillet))
    sphericalStdDevNormals(mnt,sphStd, 39)

    ## Création du Edge Density
    edgeDensity = os.path.join(rep_output, 'ED_WB_{}.tif'.format(feuillet))
    EdgeDensity(mnt, edgeDensity, 40, 5)

    # Création du Downslope Index
    DownslopeInd = os.path.join(rep_output, 'DI_WB_{}.tif'.format(feuillet))
    Downslope_Ind(MNTBreachDepression, DownslopeInd)

    ## Création du Average Normal Vector Angular Deviation
    avrNor = os.path.join(rep_output, 'ANVAD_WB_{}.tif'.format(feuillet))
    AverNormVectAngDev(mnt, avrNor, 40)

    # Création des métriques de textures d'haralick (moyenne, correlation, contraste)
    # moyenne
    mean = os.path.join(rep_output, 'MeaH_GLCM_{}.tif'.format(feuillet))
    textures_glcm(path_r, path_script, mnt, mean, '1', '39')

    # correlation
    corel = os.path.join(rep_output, 'CorH_GLCM_{}.tif'.format(feuillet))
    textures_glcm(path_r, path_script, mnt, corel, '2', '39')

    # contraste
    cont = os.path.join(rep_output, 'ConH_GLCM_{}.tif'.format(feuillet))
    textures_glcm(path_r, path_script, mnt, cont, '3', '39')

    # Suppresion des éléments du répertoire temporaire
    print('Suppression des fichiers temporaires...')
    for file in os.listdir(temp):
        os.remove(os.path.join(temp,file))
    else:
        os.rmdir(temp)
        print('Toutes les métriques ont été créées')


if __name__ == '__main__':

    # Chemin vers le mnt à traiter
    mnt = r'C:\Users\home\Documents\Documents\APP3\mnt_buffer\31H02\31H02NE_buffer.tif'
    # feuillet
    feuillet = '31H02NE'
    # Chemin vers le répertoire output des métriques
    rep_output = r'C:\Users\home\Documents\Documents\APP3\metriques'
    # Chemin vers l'application 'Rscript.exe'
    path_r = r"C:\Program Files\R\R-3.6.3\bin\Rscript.exe"
    # Chemin vers le script 'haralick.R'
    path_script = r"C:\Users\home\Documents\Documents\APP2\haralick.R"

    # Paths de SAGA
    path_saga = r'C:\Users\home\Documents\Documents\APP3\saga-7.6.3_x64\saga-7.6.3_x64'
    path_mod = r'C:\Users\home\Documents\Documents\APP3\saga-7.6.3_x64\saga-7.6.3_x64\tools'

    # Création des métriques
    creation_metriques(mnt=mnt, feuillet=feuillet, rep_output=rep_output, path_r=path_r, path_script=path_script)


