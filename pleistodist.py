import os
import numpy
import arcpy
import pandas
from getintervals import getintervals_time
from getintervals_sealvl import getintervals_sealvl
from makerasters import makerasters
from islandmode import islandmode
from individualmode import individualmode
from calcmatrices import calcmatrices_island
from calcmatrices import calcmatrices_indiv

os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = os.getcwd()
inputpath = "input/" #edit this if you want to change the input location
outpath = "output/" #edit this if you want to change the output location

#read sea level file (from Bintanja et al, 2008)
sealvl = pandas.read_csv(inputpath+'sealvl.csv')
#print(sealvl)

#input checking subroutine for time value
while True:
    try:
        #Prompt user for time cutoff input value
        time = float(raw_input("Please enter a cutoff time (kya) [0.1 to 3000, in intervals of 0.1] "))
        if 0.1 <= time <= 3000:
            break #break out of while loop if input is within accepted time range
        else:
            raise ValueError #raise exception if input is not valid
    except ValueError:
        print("Please enter a valid cutoff time") #prompt user to re-enter input, loop back to start of input checking

#input checking subroutine for interval value
while True:
    try:
        #prompt user for number of intervals
        intervals = int(raw_input("Enter the number of intervals [integer, from 1 to " + str(int(time*10))+"]: "))
        if 1 <= intervals <= (time*10): #check to see if interval value is within valid range
            break #if valid, break out of checking subroutine
        else:
            raise ValueError
    except ValueError:
        print("Please enter a valid interval value")

#input checking subroutine for binning mode
while True:
    try:
        #prompt user for number of intervals
        binningmode = int(raw_input("Do you want to generate intervals based on time [0] or by sea level [1]? "))
        if binningmode in [0,1]: #check to see if interval value is within valid range
            break #if valid, break out of checking subroutine
        else:
            raise ValueError
    except ValueError:
        print("Please enter a valid binning option (either 0 [binning by time] or 1 [binning by sea level] ")

while True:
    try:
        #prompt user for input bathymetry raster
        inputraster = raw_input("Please enter the file name of the input bathymetry raster (in .asc format) ")
        if (inputraster in os.listdir(inputpath)) & (inputraster.endswith(".asc")): #check list of files with .asc extension in input folder
            break #if user input matches file in input folder, break out of input checking subroutine
        else:
            raise ValueError
    except ValueError:
        print("Please enter a valid .asc file")

while True:
    try:
        #prompt user for point shapefile input
        points = raw_input("Enter the filename of the shapefile containing input source points ")
        if (points in os.listdir(inputpath)) & (points.endswith(".shp")):
            break
        else:
            raise ValueError
    except ValueError:
        print("Please enter a valid .shp file ")
        
while True:
    try:
        #prompt user for project projection
        epsg = int(raw_input("Enter the EPSG spatial reference value for your target area [integer between 1024 and 32767] "))
        if ((epsg >= 1024) & (epsg <= 32767)):
            break
        else:
            raise ValueError
    except ValueError:
        print("Please enter a valid EPSG reference value ")

while True:
    try:
        #prompt user for analysis mode
        mode = int(raw_input("Do you want to calculate inter-island distances [0], inter-individual distances [1], or both [2]? "))
        if mode in [0,1,2]:
            break
        else:
            raise ValueError
    except ValueError:
        print("Please choose a valid analysis mode ")

#define spatial reference presets
spatialref_default = arcpy.SpatialReference(4326)
spatialref_proj = arcpy.SpatialReference(epsg)
spatial_ref = arcpy.Describe(inputpath+points)
#check projection of point shapefile and set projection if unknown
if spatial_ref.name == "Unknown":
    print("The source points file has an unknown spatial reference, setting to default projection (EPSG 4326) ")
    arcpy.DefineProjection_management(points, spatialref_default)

#reproject shapefile to correct projection
points_projected = "sourcepoints_projected.shp"
arcpy.Project_management(inputpath+points,inputpath+points_projected,spatialref_proj)
if binningmode == 0:
    #calculate interval values and time interval counts
    getintervals_time(sealvl,time,intervals)
elif binningmode == 1:
    getintervals_sealvl(sealvl,time,intervals)
#import interval file generated by getintervals subroutine
intervalfile = pandas.read_csv(outpath+'intervals.csv')
#run subroutine to generate sea level rasters for each interval
makerasters(intervalfile,inputraster,epsg)
#run subroutine to generate distance matrices for each interval
if mode == 0:
    islandmode(intervalfile,points_projected)
    calcmatrices_island(outpath,intervalfile) #run subroutine to calculate time-weighted average across distance matrices
elif mode == 1:
    individualmode(intervalfile,points_projected)
    calcmatrices_indiv(outpath,intervalfile)
elif mode == 2:
    islandmode(intervalfile,points_projected)
    individualmode(intervalfile,points_projected)
    calcmatrices_island(outpath,intervalfile)
    calcmatrices_indiv(outpath,intervalfile)
