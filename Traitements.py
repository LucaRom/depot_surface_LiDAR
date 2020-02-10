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
for parent, dossier, fichier in os.walk(dossier_MNT):
    for mnts in fichier:

    # Path du MNT en cours
        mnt = os.path.join(parent, mnts)

    # # Création des répertoire de sortie
    #     mnt_5x5 = os.path.join(temp, 'MNT_5x5_{}.tif'.format(mnts[4:11]))
    #     mnt_corr = os.path.join(main_dir, 'MNT_5x5_corr', '{}'.format(mnts[4:9]), 'MNT_5x5_corr_{}.tif'.format(mnts[4:11]))
    #
    # # Resampling en 5x5 cubic spline
    #     resampling_cubic_spline(mnt, mnt_5x5, 5)
    #
    # # Correction hydrologique, breach depressions
    #     breachDepression(mnt_5x5, mnt_corr)
    #
    # # Suppresion des éléments du répertoire temporaire
    #     for file in os.listdir(temp):
    #         os.remove(os.path.join(temp,file))

else:
    print('Tous les fichiers ont été reéchantillonnés')


# Creation TPI, TWI et pentes
for parent, dossier, fichier in os.walk(os.path.join(os.path.join(main_dir, 'MNT_5x5_corr'))):
    for image in fichier:

    # Image de base input
        print('Ouverture image {}'.format(image))
        mnt55 = os.path.join(parent, image)

    # Création du TPI relatif avec un kernel de 200
        TPI = os.path.join(main_dir, 'TPI_WB', image[13:18], 'RelTPI_WB_{}.tif'.format(image[13:20]))
        relative_TPI(mnt55, TPI, 40)

    # # Création du SCA
    #     sca = os.path.join(temp, 'SCA_{}.tif'.format(image[13:20]))
    #     SCA(mnt55, sca)
    #
    # # Création de la pente
    #     pente = os.path.join(main_dir, 'Pente_WB', image[13:18], 'Pente_WB_{}.tif'.format(image[13:20]))
    #     slope(mnt55, pente)
    #
    # # Creation du TWI
    #     twi = os.path.join(main_dir, 'TWI_WB', image[13:18], 'TWI_WB_{}.tif'.format(image[13:20]))
    #     TWI(pente, sca, twi)

    # Suppresion des éléments du répertoire temporaire
        for file in os.listdir(temp):
            os.remove(os.path.join(temp,file))

    # Clip de la couche de dépôts


else:
    print('Tous les TPI, Pentes et TWI ont été générés')




