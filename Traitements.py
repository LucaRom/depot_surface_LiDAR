from fonctions_traitements import *
import os
import whitebox
from osgeo import gdal
from osgeo import ogr


dossier_MNT = r'C:\Users\home\Documents\Documents\APP2\mnt'


def resampling(dossier_MNT, size):

    main_dir = os.path.dirname(dossier_MNT)
    # Parcours les MNT 1x1 dans le dossier_MNT
    for parent, dossier, fichier in os.walk(dossier_MNT):
        for mnts in fichier:

        # Path du MNT en cours
            mnt = os.path.join(parent, mnts)

        # Création des répertoire de sortie
            mnt_5x5 = os.path.join(main_dir, 'MNT_5x5_cor', '{}'.format(mnts.split('_')[0]), 'MNT_5x5_cor_{}.tif'.format(mnts.split('_')[1][:-4]))

        # Resampling en 5x5 cubic spline
            resampling_cubic_spline(mnt, mnt_5x5, size)

    else:
        print('Tous les fichiers ont été reéchantillonnés')


def creation_metriques(dossier_MNT, path_r, path_script):

    # Création des répertoire auxiliaires
    main_dir = os.path.dirname(dossier_MNT)
    temp = os.path.join(main_dir, 'temp')

    for parent, dossier, fichier in os.walk(os.path.join(os.path.join(main_dir, 'MNT_5x5_cor'))):
        for image in fichier:

        # Image de base input
            print('Ouverture image {}'.format(image))
            mnt55 = os.path.join(parent, image)

        # Repertoire de sortie des metrique
            dir_metrique = os.path.join(main_dir, 'Metriques', '{}'.format(image.split('_')[3].split('.')[0][:-2]), '{}'.format(image.split('_')[3].split('.')[0]))

        # Création du TPI relatif avec un kernel de 200
            TPI = os.path.join(dir_metrique, 'TPI_WB_{}.tif'.format(image.split('_')[3][:-4]))
            relative_TPI(mnt55, TPI, 40)

        # Correction hydrologique, breach depressions pour le calcul du SCA
            MNTBreachDepression = os.path.join(temp, 'MNT_BD_{}.tif'.format(image.split('_')[3][:-4]))
            breachDepression(mnt55, MNTBreachDepression)

        # Création du SCA
            sca = os.path.join(temp, 'SCA_{}.tif'.format(image.split('_')[3][:-4]))
            SCA(MNTBreachDepression, sca)

        # Création de la pente
            pente = os.path.join(dir_metrique, 'Pen_WB_{}.tif'.format(image.split('_')[3][:-4]))
            slope(mnt55, pente)

        # Creation du TWI
            twi = os.path.join(dir_metrique, 'TWI_WB_{}.tif'.format(image.split('_')[3][:-4]))
            TWI(pente, sca, twi)

        # # Creation du plan Curvature
        #     planCur = os.path.join(dir_metrique, 'PlanCur_WB_{}.tif'.format(image.split('_')[3][:-4]))
        #     plan_curvature(mnt55, planCur)

        # Creation du profile Curvature
            profCur = os.path.join(dir_metrique, 'PC_WB_{}.tif'.format(image.split('_')[3][:-4]))
            profile_curvature(mnt55, profCur)

        # # Creation du tangential Curvature
        #     tanCur = os.path.join(dir_metrique, 'tanCur_WB_{}.tif'.format(image.split('_')[3][:-4]))
        #     tan_curvature(mnt55, tanCur)

        # Creation du Circular Variance of Aspect
            cirVar = os.path.join(dir_metrique, 'CVA_WB_{}.tif'.format(image.split('_')[3][:-4]))
            CircularVarofAspect(mnt55, cirVar, 39)

        # Création du Spherical Std Deviation of Normals
            sphStd = os.path.join(dir_metrique, 'SSDN_WB_{}.tif'.format(image.split('_')[3][:-4]))
            sphericalStdDevNormals(mnt55,sphStd, 39)

        # Création du Edge Density
            edgeDensity = os.path.join(dir_metrique, 'ED_WB_{}.tif'.format(image.split('_')[3][:-4]))
            EdgeDensity(mnt55, edgeDensity, 40, 5)

        # Création du Downslope Index
            DownslopeInd = os.path.join(dir_metrique, 'DI_WB_{}.tif'.format(image.split('_')[3][:-4]))
            Downslope_Ind(MNTBreachDepression, DownslopeInd)

        # Création du Average Normal Vector Angular Deviation
            avrNor = os.path.join(dir_metrique, 'ANVAD_WB_{}.tif'.format(image.split('_')[3][:-4]))
            AverNormVectAngDev(mnt55, avrNor, 40)

        # Création des métriques de textures d'haralick (moyenne, correlation, contraste)
            # moyenne
            mean = os.path.join(dir_metrique, 'MeaH_GLCM_{}.tif'.format(image.split('_')[3][:-4]))
            textures_glcm(path_r, path_script, mnt55, mean, '1', '3')

            # correlation
            corel = os.path.join(dir_metrique, 'CorH_GLCM_{}.tif'.format(image.split('_')[3][:-4]))
            textures_glcm(path_r, path_script, mnt55, corel, '2', '3')

            # contraste
            cont = os.path.join(dir_metrique, 'ConH_GLCM_{}.tif'.format(image.split('_')[3][:-4]))
            textures_glcm(path_r, path_script, mnt55, cont, '3', '3')

        # Suppresion des éléments du répertoire temporaire
            for file in os.listdir(temp):
                os.remove(os.path.join(temp,file))


    else:
        print('Toutes les métriques ont été créées')


if __name__ == '__main__':

    # Chemin vers le répertoire contenant les mnt à traiter
    dossier_MNT = r'C:\Users\home\Documents\Documents\APP2\mnt'
    # Chemin vers l'application 'Rscript.exe'
    path_r = r"C:\Program Files\R\R-3.6.3\bin\Rscript.exe"
    # Chemin vers le script 'haralick.R'
    path_script = r"C:\Users\home\Documents\Documents\APP2\haralick.R"

    # Prétraitements
    resampling(dossier_MNT, 50)

    # Création des métriques
    creation_metriques(dossier_MNT, path_r, path_script)


