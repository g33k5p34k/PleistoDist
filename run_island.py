import os
import arcpy
import arcpy.sa
import pandas
from arcpy.sa import *
from arcpy import env
import math
from islandmode import islandmode
env.overwriteOutput = True
#set working directory to current file directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
#set current directory as path variable
path = os.getcwd()
#set current workspace
env.workspace = path

inputpath = "input/"
outpath = "output/"

intervalfile = pandas.read_csv(outpath+'intervals.csv')
islandmode(intervalfile,"sourcepoints_projected.shp")
