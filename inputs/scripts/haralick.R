#!/usr/bin/env Rscript

# On extrait l'argument contenant le repertoire de travail
args <- commandArgs(trailingOnly = TRUE)

# On identifie les arguments en entrée
input <- args[1]
output <- args[2]
metrique <- args[3]
kernel <- strtoi(args[4])


# On verifie si les packages necessaires sont installes, sinon on les installe
print('Vérification des packages nécessaire..')
packages <- c("raster", "rgdal", "sp", "glcm")
if (length(setdiff(packages, rownames(installed.packages()))) > 0) {
  print('installation...')
  install.packages(setdiff(packages, rownames(installed.packages())), repos = "http://cran.us.r-project.org")
}

require(raster)
require(rgdal)
require(glcm)


# On identifie le traitement à effectuer selon la texture choisie
traitement = ''

if(metrique==1){
  traitement = 'mean'
}
if(metrique==2){
  traitement = 'correlation'
}
if(metrique==3){
  traitement = 'contrast'
}


# fonction du calcul des textures d'haralick
haralick <- function(input, output, traitement, kernel){
  # Calcul de la texture
  print(sprintf('Calcul de la metrique: %s...', traitement))
  texture <- glcm(raster(input, layer=1),
                  window = c(kernel,kernel),
                  statistics = c(traitement),
                  shift=list(c(0,1), c(1,1), c(1,0), c(1,-1)))
                  
  # Création du raster de sortie
  print('Sauvegarde...')
  writeRaster(texture, filename = output, format='GTiff', overwrite = TRUE)
  print('Terminé')
}

# Appel de la fonction
haralick(input, output, traitement, kernel)

