import os
import pandas
import arcpy
from arcpy import env
from arcpy.sa import *
env.overwriteOutput = True
#set working directory to current file directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
#set current directory as path variable
path = os.getcwd()
#set current workspace
env.workspace = path
#activate spatial analyst license
arcpy.CheckOutExtension("Spatial")
#define make rasters function
def makerasters(intervalfile,inputraster,epsg,outpath):
    spatialref_default = arcpy.SpatialReference(4326) #define the default GEBCO projection
    spatialref_proj = arcpy.SpatialReference(epsg) #define the projection for the project
    baseraster = arcpy.ASCIIToRaster_conversion(inputraster) #open input ASCII file and convert to raster format
    arcpy.DefineProjection_management(baseraster,spatialref_default) #set the projection of the raster to default
    arcpy.ProjectRaster_management(baseraster,outpath+"/baseraster_projected.tif",spatialref_proj,"BILINEAR") #reproject raster into correct project projection to enable accurate distance measurements
    inraster = outpath+"/baseraster_projected.tif" #load new raster
    arcpy.DefineProjection_management(inraster,spatialref_proj) #set new raster projection
    for i in intervalfile['MeanDepth'].tolist(): #iterate through Mean Depth values (1 per interval)
        x = int(intervalfile[intervalfile['MeanDepth']==i]['Interval']) #pull associated interval value for each Mean Depth value
        print("Generating island raster for interval " +str(x) + ", sea level = " + str(i)) #print status messages
        arcpy.AddMessage("Generating island raster for interval "+str(x)+", sea level = "+str(i)) #print arcpy status message
        outraster = Raster(inraster) >= i #most important part of this function -- defining land/sea boundary based on interval sea level
        outraster_reclass = Con(outraster, 1, 100, "value > 0") #convert non-land pixels to value = 100, for least cost distance analysis
        filename = "interval"+str(x) #define output name string
        arcpy.RasterToASCII_conversion(outraster_reclass,outpath+"/raster/"+filename+".asc") #save reclassed raster to ASCII file
        outraster_polygon = Con(outraster, 1, "", "value > 0") #convert non-land pixels into NODATA for polygon generation
        arcpy.RasterToPolygon_conversion(outraster_polygon,outpath+"/shapefile/"+filename+".shp") #save reclassed raster as shapefile