import os
import arcpy
import arcpy.sa
import pandas
from arcpy.sa import *
from arcpy import env
import math

env.overwriteOutput = True
#set working directory to current file directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
#set current directory as path variable
path = os.getcwd()
#set current workspace
env.workspace = path
#activate spatial analyst license
arcpy.CheckOutExtension("Spatial")
#define layer names
sourcepoints = "sourcepoints"

#this function calculates the Euclidean distance between points (time-invariant), and the least cost distance between points over time.
def individualmode(intervalfile, points):
    os.mkdir("scratch")
    #load point shapefile
    arcpy.MakeFeatureLayer_management("input/"+points,sourcepoints)
    #calculate the number of points contained in point shapefile
    FIDmax = arcpy.GetCount_management(sourcepoints)
    #generate array of FID values from point shapefile
    FIDrange = range(0,int(FIDmax[0]))
    #create header string for output distance matrices
    header = "FID,"+",".join(map(str,FIDrange))+"\n"
    #setup search cursors for source and destination points
    source = arcpy.da.SearchCursor(sourcepoints,["FID","SHAPE@","SHAPE@X","SHAPE@Y"])
    sink = arcpy.da.SearchCursor(sourcepoints,["FID","SHAPE@","SHAPE@X","SHAPE@Y"])
    #start looping through interval file
    for i in intervalfile['Interval'].tolist(): #convert interval column into list and iterate through each interval
        if i == 0: #for interval 0, calculate euclidean distance between points and least cost distance
            #open output files and write header row
            f = open("output/individual_euclidean_interval0.csv","w")
            g = open("output/individual_leastcost_interval0.csv","w")
            f.write(header)
            g.write(header)
            for pf in source: #start first order for loop for origin points
                euclideandist = [str(pf[0])] #write source point FID as first value to container variable
                for pt in sink:
                    eucdist = pf[1].distanceto(pt[1]) #calculate euclidean distance between points
                    euclideandist.append(eucdist) #write value to container variable
                    strSQL1 = """ "FID" = {0}""".format(pf[0]) #define SQL search string for source point
                    strSQL2 = """ "FID" = {0}""".format(pt[0]) #define SQL search string for destination point

                    arcpy.ASCIIToRaster("output/raster/interval0.asc","scratch/interval0.tiff") #convert cost raster into a readable format
                    inraster = "scratch/interval0.tiff" #load cost raster
                    arcpy.DefineProjection_management(inraster,"output/raster/interval0.prj") #set projection of input raster
                    