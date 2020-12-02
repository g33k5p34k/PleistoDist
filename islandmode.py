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
intervalshp = "intervalshp"

#this workhorse module calculates the normalised distance over time between islands based on input points. 
def islandmode(intervalfile,points):
    os.chdir(path)
    #load point shapefile 
    arcpy.MakeFeatureLayer_management("input/"+points,sourcepoints)
    #calculate the number of points contained in point shapefile
    FIDmax = arcpy.GetCount_management(sourcepoints)
    #generate array of FID values from point shapefile
    FIDrange = range(0,int(FIDmax[0]))
    #create header string for output distance matrices
    header = "FID,"+",".join(map(str,FIDrange))+"\n"
    #setup search cursors for source and destination points
    source = arcpy.da.SearchCursor(sourcepoints,["FID"])
    sink = arcpy.da.SearchCursor(sourcepoints,["FID"])
    #start looping through interval file
    for i in intervalfile['Interval'].tolist(): #convert interval column into list and iterate through each interval
        arcpy.MakeFeatureLayer_management("output/shapefile/interval"+str(i)+".shp",intervalshp)
        print("Preparing distance matrix for interval: "+ str(i))
        #open Euclidean centroid distance matrix file and write header
        f = open("output/islandcentroid_euclidean_interval"+str(i)+".csv","w")
        f.write(header)
        #open least overwater distance matrix file and write header
        g = open("output/island_leastdist_interval"+str(i)+".csv","w")
        g.write(header)
        for pf in source: #start of 1st order for-loop for origin points
            #append FID value to first column in row for each distance matrix type
            euccentroid = [str(pf[0])]
            leastdist = [str(pf[0])]
            for pt in sink: #start of 2nd order for-loop for destination points
                print("Source point: "+ str(pf[0])+ "; Sink point: " + str(pt[0]))
                if pf == pt: #set NA value for self-to-self comparisons
                    euccentroid.append("NA")
                    leastdist.append("NA")
                else:
                    strSQL1 = """ "FID" = {0}""".format(pf[0]) #define SQL search string for source point
                    strSQL2 = """ "FID" = {0}""".format(pt[0]) #define SQL search string for destination point
                    arcpy.SelectLayerByAttribute_management(sourcepoints,"NEW_SELECTION",strSQL1) #select source point in sourcepoints shapefile 
                    arcpy.SelectLayerByLocation_management(intervalshp,"INTERSECT",sourcepoints, selection_type = "NEW_SELECTION") #using source point, select the overlapping polygon on the intervalshp shapefile
                    if int(arcpy.GetCount_management(intervalshp).getOutput(0)) < 1: #test to see if point is below sea level, write NA if true
                        print("Point "+str(pf[0])+" is below sea level during interval "+str(i)+", writing distance value of NA")
                        euccentroid.append("NA")
                        leastdist.append("NA")
                    else:
                        arcpy.SelectLayerByAttribute_management(sourcepoints,"ADD_TO_SELECTION",strSQL2) #if source point is on valid landmass, select destination point in sourcepoints shapefile
                        arcpy.SelectLayerByLocation_management(intervalshp,"INTERSECT",sourcepoints, selection_type = "ADD_TO_SELECTION") #select island polygon based on destination point
                        if int(arcpy.GetCount_management(intervalshp).getOutput(0)) == 1: #two possibilities here: either both points lie on the same island or the destination point is underwater
                            arcpy.SelectLayerByAttribute_management(sourcepoints,"NEW_SELECTION",strSQL2) #reselect destination point as a new selection
                            arcpy.SelectLayerByLocation_management(intervalshp,"INTERSECT",sourcepoints,selection_type = "REMOVE_FROM_SELECTION") #based on destination point, remove intersecting island polygon from selection
                            if int(arcpy.GetCount_management(intervalshp).getOutput(0))  == 1: #if there is no change to the number of selected polygons, then the destination point is underwater, write NA value.
                                print("Destination point "+str(pt[0])+" is underwater, writing a distance value of NA")
                                euccentroid.append("NA")
                                leastdist.append("NA")
                            else: #otherwise, write distance of 0 since both points are on the same island. 
                                print("Points "+str(pf[0])+" and "+str(pt[0])+" are on the same landmass, printing distance of 0")
                                euccentroid.append(str(0))
                                leastdist.append(str(0))
                        else: #if both points are on different islands, proceed to calculate inter-island distance
                            cursor = arcpy.da.SearchCursor(intervalshp,["SHAPE@XY","SHAPE@"]) #create search cursor within island polygon shapefile, with centroid and geometry as fields
                            centroid = []
                            geometry = []
                            for a in cursor:
                                centroid.append(a[0]) #create array of centroid values
                                geometry.append(a[1]) #create array of geometries
                            eucdist_var = math.sqrt(((centroid[1][0]-centroid[0][0])**2) + ((centroid[1][1]-centroid[0][1])**2)) #calculate euclidean distance between centroids using Pythagoras' Theorem
                            leastdist_var = geometry[0].distanceTo(geometry[1]) #calculate least distance between geometries
                            euccentroid.append(str(eucdist_var)) #append euclidean distance between centroids to file
                            leastdist.append(str(leastdist_var)) #append least distance between islands to file
                            del cursor #clear memory
            euclideancentroid = ','.join(euccentroid)
            leastdistance = ','.join(leastdist)
            f.write(euclideancentroid+"\n")
            g.write(leastdistance+"\n")
            sink.reset()
        f.close()
        g.close()
        source.reset()
    del source
    del sink
