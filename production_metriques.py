from fonctions_metriques import *
import os


def creation_metriques(rep_mnt, rep_output, path_r, path_script):

    # Création des répertoire de sortie et temporaires
    temp = os.path.join(rep_output, 'temp')

    for parent, dossier, fichier in os.walk(rep_mnt):
        for image in fichier:

        # Image de base input
            print('Ouverture image {}'.format(image))
            mntBuff = os.path.join(parent, image)

        # Extraction du nom du feuillet
            feuillet = image.split('_')[0][:-2]
            division_feuillet = image.split('_')[0]

        # Repertoire de sortie des metrique
            #dir_metrique = os.path.join(main_dir, 'Metriques', '{}'.format(image.split('_')[3].split('.')[0][:-2]), '{}'.format(image.split('_')[3].split('.')[0]))
            dir_metrique =os.path.join(rep_output, feuillet, division_feuillet)

        # Création du TPI relatif avec un kernel de 200
            TPI = os.path.join(dir_metrique, 'TPI_WB_{}.tif'.format(division_feuillet))
            relative_TPI(mntBuff, TPI, 40)

        # Correction hydrologique, breach depressions pour le calcul du SCA
            MNTBreachDepression = os.path.join(temp, 'MNT_BD_{}.tif'.format(division_feuillet))
            breachDepressionLeastCost(mntBuff, MNTBreachDepression, 40, True)

        # Création du SCA
            sca = os.path.join(temp, 'SCA_{}.tif'.format(division_feuillet))
            SCA(MNTBreachDepression, sca)

        # Création de la pente
            pente = os.path.join(dir_metrique, 'Pen_WB_{}.tif'.format(division_feuillet))
            slope(mntBuff, pente)

        # Creation du TWI
            twi = os.path.join(dir_metrique, 'TWI_WB_{}.tif'.format(division_feuillet))
            TWI(pente, sca, twi)

        # # Creation du plan Curvature
        #     planCur = os.path.join(dir_metrique, 'PlanCur_WB_{}.tif'.format(image.split('_')[3][:-4]))
        #     plan_curvature(mnt55, planCur)

        # Creation du profile Curvature
            profCur = os.path.join(dir_metrique, 'PC_WB_{}.tif'.format(division_feuillet))
            profile_curvature(mntBuff, profCur)

        # # Creation du tangential Curvature
        #     tanCur = os.path.join(dir_metrique, 'tanCur_WB_{}.tif'.format(division_feuillet))
        #     tan_curvature(mntBuff, tanCur)

        # Creation du Circular Variance of Aspect
            cirVar = os.path.join(dir_metrique, 'CVA_WB_{}.tif'.format(division_feuillet))
            CircularVarofAspect(mntBuff, cirVar, 39)

        # Création du Spherical Std Deviation of Normals
            sphStd = os.path.join(dir_metrique, 'SSDN_WB_{}.tif'.format(division_feuillet))
            sphericalStdDevNormals(mntBuff,sphStd, 39)

        # Création du Edge Density
            edgeDensity = os.path.join(dir_metrique, 'ED_WB_{}.tif'.format(division_feuillet))
            EdgeDensity(mntBuff, edgeDensity, 40, 5)

        # Création du Downslope Index
            DownslopeInd = os.path.join(dir_metrique, 'DI_WB_{}.tif'.format(division_feuillet))
            Downslope_Ind(MNTBreachDepression, DownslopeInd)

        # Création du Average Normal Vector Angular Deviation
            avrNor = os.path.join(dir_metrique, 'ANVAD_WB_{}.tif'.format(division_feuillet))
            AverNormVectAngDev(mntBuff, avrNor, 40)

        # Création des métriques de textures d'haralick (moyenne, correlation, contraste)
            # moyenne
            mean = os.path.join(dir_metrique, 'MeaH_GLCM_{}.tif'.format(division_feuillet))
            textures_glcm(path_r, path_script, mntBuff, mean, '1', '39')

            # correlation
            corel = os.path.join(dir_metrique, 'CorH_GLCM_{}.tif'.format(division_feuillet))
            textures_glcm(path_r, path_script, mntBuff, corel, '2', '39')

            # contraste
            cont = os.path.join(dir_metrique, 'ConH_GLCM_{}.tif'.format(division_feuillet))
            textures_glcm(path_r, path_script, mntBuff, cont, '3', '39')

        # Suppresion des éléments du répertoire temporaire
            print('Suppression des fichiers temporaires...')
            for file in os.listdir(temp):
                os.remove(os.path.join(temp,file))


    else:
        print('Toutes les métriques ont été créées')


if __name__ == '__main__':

    # Chemin vers le répertoire contenant les mnt à traiter
    rep_mnt = r'C:\Users\home\Documents\Documents\APP3\mnt_buffer'
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
    creation_metriques(rep_mnt=rep_mnt, rep_output=rep_output, path_r=path_r, path_script=path_script)


