# -*- coding: utf-8 -*-

"""
Created on Wed Jan 2020
@author: Luca Romanini

"""

# Import des librairies
from datetime import datetime
import geopandas as gpd
import numpy as np
import os, osr
from osgeo import gdal
from gdalconst import *
import pandas as pd
import time
import getopt
import sys

# Pour modèle de classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier


#### Entraînement du modèle de classification ####

def entrainement (inputEch, metriques):
    # Pour importer un shapefile
    # Chemin vers le dossier avec les shapefiles d'entrainement
    #folder_path = os.path.join(root_dir, 'inputs/inputs_modele_avril2020')

    # # On crée la liste des shapefiles
    files = os.listdir(inputEch)  # Liste des fichiers dans le dossier "folder"
    shp_list = [os.path.join(inputEch, i) for i in files if i.endswith('.shp')] # Obtenir une liste des chemins pour
                                                                                   # .shp seulement
    # On join les fichiers .shp de la liste
    new_shp = gpd.GeoDataFrame(pd.concat([gpd.read_file(i) for i in shp_list],
                                          ignore_index = True), crs = gpd.read_file(shp_list[0]).crs)

    # On choisi la colonne de que l'on veut prédire (ici le type de dépots)
    y_depots = new_shp.Zone

    # On definit les métriques sur lesquels on veut faire l'analyse
    X_metriques = new_shp[metriques]

    # Séparation des données en données d'entrainement et données de tests
    train_metriques, test_metriques, train_y, test_y = train_test_split(X_metriques, y_depots, test_size = 0.30, random_state = 42)

    # Create a Gaussian Classifier
    clf = RandomForestClassifier(n_estimators = 500, verbose = 2, oob_score = True, random_state = 42)

    # Train the model using the training sets y_pred=clf.predict(X_test)
    clf.fit(train_metriques, train_y)     # Model fit sur 70%
    #y_pred = clf.predict(test_metriques)  # Predicition sur 30%

    return clf

    #### FIN ENTRAINEMENT MODELE ####


def classification (clf, tiffs_list):

    # On crée la stack de métrique
    # met_stack = np.stack(tiffs_list)
    met_stack = np.dstack(tiffs_list)

    # On met la stack en 2 dimensions pour pouvoir faire le model dessus
    rows, cols, bands = met_stack.shape
    data2d = np.reshape(met_stack, (rows * cols, bands))

    # Prediction du modèle et on le reshape
    prediction = clf.predict(data2d)
    prediction = np.reshape(prediction, (rows, cols))

    return prediction


def creation_output (prediction, outputdir, nom_fichier, inputMet, tiff_path_list, start):
    # On crée une image GEOTIFF en sortie
    # je déclare tous les drivers
    gdal.AllRegister()
    # le driver que je veux utiliser GEOTIFF
    driver = gdal.GetDriverByName("GTiff")

    # taille de mon image (ce sera la taille de la matrice)
    rows, cols = prediction.shape

    # je déclare mon image
    # il faut : la taille, le nombre de bandes et le type de données (ce sera des bytes)
    image = driver.Create((os.path.join(outputdir, nom_fichier)), cols, rows, 1, GDT_Byte)

    # J'extrais les paramètres d'une métriques pour le positionnement du fichier sortant
    data = gdal.Open(os.path.join(inputMet, tiff_path_list[0]))

    # J'applique les paramètres de positionnement
    geoTransform = data.GetGeoTransform()
    data = None # On vide la mémoire

    # On donne la coordonnée d'origine de l'image raster tiré d'une des métriques
    image.SetGeoTransform(geoTransform)

    # je cherche la bande 1
    band = image.GetRasterBand(1)

    # Je remets la matrice en 2 dimension
    # result1 = resultat.reshape(resultat.shape[1], resultat.shape[2])
    result1 = prediction.reshape(prediction.shape[0], prediction.shape[1])

    # j'écris la matrice dans la bande
    # band.WriteArray(result1, 0, 0)
    band.WriteArray(prediction, 0, 0)

    # Je définis la projection
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(2950)

    image.SetProjection(outRasterSRS.ExportToWkt())

    # je vide la cache
    band.FlushCache()
    band.SetNoDataValue(-99)
    # j'efface ma matrice
    del prediction
    del band
    del image

    print("Fin de la classification")

    # Impression du temps
    end = time.time()
    elapsed = end - start
    print("Elapsed time : %.2f s" % (elapsed))

    #### FIN SCRIPT ET PROJET GEOINFO ####


def main(argv):
    root_dir = os.path.abspath(os.path.dirname(__file__))
    erreur1 = "Il manque des arguments. Assurez vous de bien avoir fournie les trois arguments -e -m et -o"

    inputEch, inputMet, outputdir = "","",""   # Paramètres à fournir par l'utilisateur

    opts = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hde:m:o:", ["help", "defaultPaths", "inputEchant=","inputMetriques=", "output="])
        # print(args)
        # print(opts)
    except getopt.GetoptError as err:
        print(err)
        print("Pour l'aide, utiliser -h ou --help")
        sys.exit(2)

    # Répertoires input/output
    if len(opts) == 0:                       # On teste d'abord s'il n'y a aucun argument
        print(erreur1)
        sys.exit(2)
    elif opts[0][0] in ("-h", "--help"):     # On test si l'utilisateur demande l'aide
        print("voici l'aide")
        sys.exit(2)
    elif opts[0][0] in ("-d", "--defaultPaths"):     # On test si l'utilisateur veut les chemins par défauts
        inputEch  = os.path.join(root_dir, 'inputs/inputs_modele_avril2020')
        inputMet  = os.path.join(root_dir, 'inputs/tiffs/31H02NE_50m')
        outputdir = os.path.join(root_dir, 'outputs/projet_geo_info')
    elif len(opts) < 3 or len(args) < 3:             # Si l'utilisateur à moins de 3 arguments et n'a pas demandé d'aide
        print(erreur1)
        sys.exit(2)
    else:                                            # Si les trois inputs sont entrées, on part le script
        for o, a in opts:
            if o in ("-e", "--inputEchant"):
                inputEch = a
            elif o in ("-m", "--inputMetriques"):
                inputMet = a
            elif o in ("-o", "--output"):
                outputdir = a
        print(inputEch, inputMet, outputdir)

    #### PARAMETRES INITIAUX ####

    # On définit le dossier parent pour le réutiliser dans l'import d'intrants
    root_dir = os.path.abspath(os.path.dirname(__file__))

    # On ajoute la date au fichier sortant pour un meilleur suivi
    date_classi = str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))

    #### PARAMETRES À FOURNIR ####

    # Structure du nom du fichier sortant
    nom_fichier = 'modele_predit_pixel' + date_classi + '.tiff'

    # # Liste des métriques pour l'analyse
    # # metriques = ['DI', 'MeanHar', 'Pente', 'TPI']
    metriques = ['ANVAD', 'CVA', 'ContHar', 'CorHar', 'DI', 'EdgeDens', 'MeanHar', 'Pente', 'ProfCur', 'TPI', 'SSDN',
                 'TWI']

    ## DÉBUT DES TRAITEMENTS####
    # On démarre le compteur pour cette section
    # Calcul du temps
    start = time.time()
    print("Debut de la classification")
    print("start")

    # Import des images en matrices numpy
    tiff_path_list = os.listdir(inputMet)  # Liste des fichiers

    # On crée une liste avec toutes les images lues
    tiffs_list = []
    for i in tiff_path_list:
        ds = gdal.Open(os.path.join(inputMet, i))
        tiffs_list.append(ds.GetRasterBand(1).ReadAsArray())

    # shapeimg1 = met4.shape
    # for i in image_list:
    #     if i.shape != shapeimg1:
    #         print("Les images ne sont pas de la même taille")
    #         print(i)
    #         break
    #     else:
    #         print("Ok!")

    # Entraînement du modèle
    ent = entrainement(inputEch=inputEch, metriques=metriques)

    # Classification selon les métriques
    classif = classification(clf=ent, tiffs_list=tiffs_list)

    # Création du fichier de sortie
    creation_output(prediction=classif, outputdir=outputdir , nom_fichier=nom_fichier,
                    inputMet=inputMet, tiff_path_list=tiff_path_list, start=start)


if __name__ == "__main__":
    main(sys.argv[1:])