setwd('C:/Users/home/Documents/Documents/APP2')
path_NE <- 'MNT_31H02NE_5x5.tif'
path_SE <- 'MNT_31H02SE_5x5.tif'
path_SO <- 'MNT_31H02SO_5x5.tif'

require(raster)
require(rgdal)


# Mean_SE <- glcm(raster(path_ras, layer=1), window = c(39,39), statistics = c('mean'), shift=list(c(0,1), c(1,1), c(1,0), c(1,-1)))
# plot(Mean_SE)
# writeRaster(Mean_SE, filename = 'Mean_31H02SE.tif', format='GTiff', overwrite = TRUE)
# 
# Contrast_SE <- glcm(raster(path_ras, layer=1), window = c(39,39), statistics = c('contrast'), shift=list(c(0,1), c(1,1), c(1,0), c(1,-1)))
# plot(Contrast_SE)
# writeRaster(Contrast_SE, filename = 'Contrast_31H02SE.tif', format='GTiff', overwrite = TRUE)

# correl_NE <- glcm(raster(path_NE, layer=1), window = c(39,39), statistics = c('correlation'), shift=list(c(0,1), c(1,1), c(1,0), c(1,-1)))
# plot(correl_NE)
# writeRaster(correl_NE, filename = 'correl_GLCM_31H02NE.tif', format='GTiff', overwrite = TRUE)
# 
# correl_SE <- glcm(raster(path_SE, layer=1), window = c(39,39), statistics = c('correlation'), shift=list(c(0,1), c(1,1), c(1,0), c(1,-1)))
# plot(correl_SE)
# writeRaster(correl_SE, filename = 'correl_GLCM_31H02SE.tif', format='GTiff', overwrite = TRUE)



# Feuillet 31H02SO

Contrast_SO <- glcm(raster(path_SO, layer=1), window = c(39,39), statistics = c('contrast'), shift=list(c(0,1), c(1,1), c(1,0), c(1,-1)))
plot(Contrast_SO)
writeRaster(Contrast_SO, filename = 'Contrast_GLCM_31H02SO.tif', format='GTiff', overwrite = TRUE)

Mean_SO <- glcm(raster(path_SO, layer=1), window = c(39,39), statistics = c('mean'), shift=list(c(0,1), c(1,1), c(1,0), c(1,-1)))
plot(Mean_SO)
writeRaster(Mean_SO, filename = 'Mean_GLCM_31H02SO.tif', format='GTiff', overwrite = TRUE)

correl_SO <- glcm(raster(path_SO, layer=1), window = c(39,39), statistics = c('correlation'), shift=list(c(0,1), c(1,1), c(1,0), c(1,-1)))
plot(correl_SO)
writeRaster(correl_SO, filename = 'correl_GLCM_31H02SO.tif', format='GTiff', overwrite = TRUE)

