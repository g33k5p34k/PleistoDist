import os
import numpy
import arcpy
import pandas
from getintervals import getintervals_time
from getintervals_sealvl import getintervals_sealvl
from makerasters import makerasters
from islandmode import islandmode
from calcmatrices import calcmatrices
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#set current directory as path variable
path = os.getcwd()
#set current workspace
arcpy.env.workspace = path
arcpy.env.overwriteOutput = True

#read sea level file (from Bintanja et al, 2008)
sealvl = pandas.read_csv('../ToolData/sealvl.csv')
#print(sealvl)

#setupoutput folder
outpath = arcpy.GetParameterAsText(0)
os.mkdir(outpath)
shapepath = outpath+r'\shapefile'
rasterpath = outpath+r'\raster'
#setup folder structure in output folder
if not os.path.exists(shapepath):
    os.mkdir(shapepath)
if not os.path.exists(rasterpath):
    os.mkdir(rasterpath)

#define inputs
time = float(arcpy.GetParameterAsText(1))
intervals = int(arcpy.GetParameterAsText(2))
binningmode = arcpy.GetParameterAsText(3)
inputraster = arcpy.GetParameterAsText(4)
points = arcpy.GetParameterAsText(5)
epsg = int(arcpy.GetParameterAsText(6))

#input checking subroutines
if intervals > (time * 10):
    arcpy.AddError("The Interval value is too high!")
    raise arcpy.ExecuteError
if int(arcpy.GetCount_management(points)[0]) < 2:
    arcpy.AddError("Please ensure that there are more than 2 points in your input file")
    raise arcpy.ExecuteError

#define spatial reference presets
spatialref_default = arcpy.SpatialReference(4326)
spatialref_proj = arcpy.SpatialReference(epsg)
spatial_ref = arcpy.Describe(points)
#check projection of point shapefile and set projection if unknown
if spatial_ref.name == "Unknown":
    print("The source points file has an unknown spatial reference, setting to default projection (EPSG 4326) ")
    arcpy.DefineProjection_management(points, spatialref_default)

#reproject shapefile to correct projection
points_projected = outpath+"sourcepoints_projected.shp"
arcpy.Project_management(points,points_projected,spatialref_proj)

#calculate interval values and time interval counts
if binningmode == "Time":
    getintervals_time(sealvl,time,intervals,outpath)
else:
    getintervals_sealvl(sealvl,time,intervals,outpath)
#import interval file generated by getintervals subroutine
intervalfile = pandas.read_csv(outpath+'/intervals.csv')
#run subroutine to generate sea level rasters for each interval
makerasters(intervalfile,inputraster,epsg,outpath)
#run subroutine to generate distance matrices for each sea level interval
islandmode(intervalfile,points_projected,outpath)
#run subroutine to calculate time-weighted average across distance matrices
calcmatrices(outpath,intervalfile)
