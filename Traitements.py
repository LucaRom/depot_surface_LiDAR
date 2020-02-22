from fonctions_traitements import *
import os
import whitebox
from osgeo import gdal
from osgeo import ogr


dossier_MNT = r'D:\DATA\MNT'

# Répertoire racine
main_dir = os.path.dirname(dossier_MNT)
temp = os.path.join(main_dir, 'temp')

# Resampling et correction hydrologique
# Parcours les MNT 1x1 dans le dossier_MNT
# for parent, dossier, fichier in os.walk(dossier_MNT):
#     for mnts in fichier:
#
#     # Path du MNT en cours
#         mnt = os.path.join(parent, mnts)
#
#     # Création des répertoire de sortie
#         mnt_5x5 = os.path.join(temp, 'MNT_5x5_{}.tif'.format(mnts[4:11]))
#         mnt_cor = os.path.join(main_dir, 'MNT_5x5_cor', '{}'.format(mnts[4:9]), 'MNT_5x5_cor_{}.tif'.format(mnts[4:11]))
#
#
#     # Resampling en 5x5 cubic spline
#         resampling_cubic_spline(mnt, mnt_5x5, 5)
#
#     # Filtrage du MNT 5x5 FPDEMS
#         fpdems(mnt_5x5, mnt_cor)
#         #gdal_translate_32to64(fpdems32, mnt_cor)
#
#     # Suppresion des éléments du répertoire temporaire
#         for file in os.listdir(temp):
#             os.remove(os.path.join(temp,file))
#
# else:
#     print('Tous les fichiers ont été reéchantillonnés')


# Creation des métriques
for parent, dossier, fichier in os.walk(os.path.join(os.path.join(main_dir, 'MNT_5x5_cor'))):
    for image in fichier:

    # Image de base input
        print('Ouverture image {}'.format(image))
        mnt55 = os.path.join(parent, image)

    # Repertoire de sortie des metrique
        dir_metrique = os.path.join(main_dir, 'Metriques', '{}'.format(image[12:17]), '{}'.format(image[12:19]))

    # Création du TPI relatif avec un kernel de 200
        TPI = os.path.join(dir_metrique, 'RelTPI_WB_{}'.format(image[12:19]))
        relative_TPI(mnt55, TPI, 40)

    # Correction hydrologique, breach depressions pour le calcul du SCA
        MNTBreachDepression = os.path.join(temp, 'MNT_BD_{}.tif'.format(image[12:19]))
        breachDepression(mnt55, MNTBreachDepression)

    # Création du SCA
        sca = os.path.join(temp, 'SCA_{}.tif'.format(image[12:19]))
        SCA(MNTBreachDepression, sca)

    # Création de la pente
        pente = os.path.join(dir_metrique, 'Pente_WB_{}.tif'.format(image[12:19]))
        slope(mnt55, pente)

    # Creation du TWI
        twi = os.path.join(dir_metrique, 'TWI_WB_{}.tif'.format(image[12:19]))
        TWI(pente, sca, twi)

    # Creation du plan Curvature
        planCur = os.path.join(dir_metrique, 'PlanCur_WB_{}.tif'.format(image[12:19]))
        plan_curvature(mnt55, planCur)

    # Creation du profile Curvature
        profCur = os.path.join(dir_metrique, 'ProfCur_WB_{}.tif'.format(image[12:19]))
        profile_curvature(mnt55, profCur)

    # Creation du tangential Curvature
        tanCur = os.path.join(dir_metrique, 'tanCur_WB_{}.tif'.format(image[12:19]))
        tan_curvature(mnt55, tanCur)

    # Creation du Circular Variance of Aspect
        cirVar = os.path.join(dir_metrique, 'CirVarAsp_WB_{}.tif'.format(image[12:19]))
        CircularVarofAspect(mnt55, cirVar)

    # Création du Spherical Std Deviation of Normals
        sphStd = os.path.join(dir_metrique, 'SphStdDevNor_WB_{}.tif'.format(image[12:19]))
        sphericalStdDevNormals(mnt55,sphStd)

    # Création du Edge Density
        edgeDensity = os.path.join(dir_metrique, 'EdgeDens_WB_{}.tif'.format(image[12:19]))
        EdgeDensity(mnt55, edgeDensity)

    # Création du Downslope Index
        DownslopeInd = os.path.join(dir_metrique, 'DownslopeInd_WB_{}.tif'.format(image[12:19]))
        Downslope_Ind(MNTBreachDepression, DownslopeInd)

    # Création du Average Normal Vector Angular Deviation
        avrNor = os.path.join(dir_metrique, 'AvrNorVecAngDev_WB_{}.tif'.format(image[12:19]))
        AverNormVectAngDev(mnt55, avrNor)



    # Suppresion des éléments du répertoire temporaire
        for file in os.listdir(temp):
            os.remove(os.path.join(temp,file))


else:
    print('Toutes les métriques ont été créées')




