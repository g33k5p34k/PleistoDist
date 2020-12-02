import os
import arcpy
import arcpy.sa
import pandas
from arcpy.sa import *
from arcpy import env
import math
import shutil

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

#this function calculates the Euclidean distance between points (time-invariant), and the least cost distance between points over time.
def individualmode(intervalfile,points,outpath):
    if os.path.exists("Scratch"):
        arcpy.AddMessage("Using existing scratch folder")
    else:
        os.mkdir("Scratch")
    #load point shapefile
    arcpy.MakeFeatureLayer_management(points,sourcepoints)
    #calculate the number of points contained in point shapefile
    FIDmax = arcpy.GetCount_management(sourcepoints)
    #generate array of FID values from point shapefile
    FIDrange = range(0,int(FIDmax[0]))
    #create header string for output distance matrices
    header = "FID,"+",".join(map(str,FIDrange))+"\n"
    
    #start looping through interval file
    for i in intervalfile['Interval'].tolist(): #convert interval column into list and iterate through each interval
        if i == 0: #because Euclidean distance between points should only be calculated for the first interval, run interval0 separately
            arcpy.AddMessage("Calculating outputs for interval "+ str(i))
            #setup search cursors for source and destination points
            source = arcpy.da.SearchCursor(sourcepoints,["FID","SHAPE@","SHAPE@X","SHAPE@Y"])
            sink = arcpy.da.SearchCursor(sourcepoints,["FID","SHAPE@","SHAPE@X","SHAPE@Y"])
            arcpy.MakeFeatureLayer_management(outpath+"/shapefile/interval0.shp",intervalshp) #load island polygon for interval 0
            #open output files and write header row
            f = open(outpath+"/individual_euclidean_interval0.csv","w") #this output file is for the inter-point Euclidean distance
            g = open(outpath+"/individual_leastcost_interval0.csv","w") #this output file is for the least-cost path distance
            f.write(header)
            g.write(header)
            inraster = arcpy.ASCIIToRaster_conversion(outpath+"/raster/interval0.asc") #convert cost raster into a readable format
            arcpy.DefineProjection_management(inraster,outpath+"/raster/interval0.prj") #set projection of input raster
            for pf in source: #start first order for loop for origin points
                euclideandist = [str(pf[0])] #write source point FID as first value to container variable
                leastcostdist = [str(pf[0])] #write source point FID as first value to container variable
                for pt in sink: #start second order for loop for destination points
                    if pf == pt: #set distance to NA for self-comparisons
                        euclideandist.append("NA")
                        leastcostdist.append("NA")
                    else: #this subroutine checks for submerged points
                        strSQL1 = """ "FID" = {0}""".format(pf[0]) #define SQL search string for source point
                        strSQL2 = """ "FID" = {0}""".format(pt[0]) #define SQL search string for destination point
                        arcpy.SelectLayerByAttribute_management(sourcepoints,"NEW_SELECTION",strSQL1) #select source point in sourcepoints shapefile 
                        arcpy.SelectLayerByLocation_management(intervalshp,"INTERSECT",sourcepoints, selection_type = "NEW_SELECTION") #using source point, select the overlapping polygon on the intervalshp shapefile
                        if int(arcpy.GetCount_management(intervalshp).getOutput(0)) < 1: #test to see if point is below sea level, write NA if true
                            arcpy.AddMessage("Point "+str(pf[0])+" is below sea level during interval "+str(i)+", writing distance value of NA")
                            euclideandist.append("NA") #write NA if source point is submerged
                            leastcostdist.append("NA")
                        else:
                            arcpy.SelectLayerByAttribute_management(sourcepoints,"ADD_TO_SELECTION",strSQL2) #if source point is on valid landmass, select destination point in sourcepoints shapefile
                            arcpy.SelectLayerByLocation_management(intervalshp,"INTERSECT",sourcepoints, selection_type = "ADD_TO_SELECTION") #select island polygon based on destination point
                            if int(arcpy.GetCount_management(intervalshp).getOutput(0)) == 1: #two possibilities here: either both points lie on the same island or the destination point is underwater
                                arcpy.SelectLayerByAttribute_management(sourcepoints,"NEW_SELECTION",strSQL2) #reselect destination point as a new selection
                                arcpy.SelectLayerByLocation_management(intervalshp,"INTERSECT",sourcepoints,selection_type = "REMOVE_FROM_SELECTION") #based on destination point, remove intersecting island polygon from selection
                                if int(arcpy.GetCount_management(intervalshp).getOutput(0))  == 1: #if there is no change to the number of selected polygons, then the destination point is underwater, write NA value.
                                    arcpy.AddMessage("Destination point "+str(pt[0])+" is underwater, writing a distance value of NA")
                                    euclideandist.append("NA") #write NA if sink point is submerged. 
                                    leastcostdist.append("NA")
                                else:
                                    eucdist = math.sqrt(((pt[2]-pf[2])**2)+((pt[3]-pf[3])**2)) #calculate euclidean distance between points
                                    arcpy.AddMessage("The Euclidean distance between point " + str(pf[0]) + " and point " + str(pt[0])+ " is " + str(eucdist))
                                    euclideandist.append(str(eucdist)) #write value to container variable
                                    arcpy.SelectLayerByAttribute_management(sourcepoints,"NEW_SELECTION",strSQL1) #reselect source point in sourcepoints layer 
                                    costdist = CostDistance(sourcepoints,inraster,"","Scratch/backlink") #generate cost distance raster for source point
                                    arcpy.SelectLayerByAttribute_management(sourcepoints,"NEW_SELECTION",strSQL2) #now select destination point in sourcepoints layer
                                    arcpy.sa.CostPathAsPolyline(sourcepoints,costdist,"Scratch/backlink","Scratch/leastcostline.shp") #calculate least cost path from source to destination
                                    with arcpy.da.SearchCursor("Scratch/leastcostline.shp","SHAPE@LENGTH") as cursor: #open least cost line and calculate length
                                        for line in cursor:
                                            leastcostdist.append(str(line[0])) #write length to container variable
                                            arcpy.AddMessage("The least cost distance between point " + str(pf[0]) + " and point " + str(pt[0])+ " is " + str(line[0]))
                                    del cursor
                            else: #either the points are on the same island or on different islands
                                eucdist = math.sqrt(((pt[2]-pf[2])**2)+((pt[3]-pf[3])**2)) #calculate euclidean distance between points
                                arcpy.AddMessage("The Euclidean distance between point " + str(pf[0]) + " and point " + str(pt[0])+ " is " + str(eucdist))
                                euclideandist.append(str(eucdist)) #write value to container variable
                                arcpy.SelectLayerByAttribute_management(sourcepoints,"NEW_SELECTION",strSQL1) #reselect source point in sourcepoints layer 
                                costdist = CostDistance(sourcepoints,inraster,"","Scratch/backlink") #generate cost distance raster for source point
                                arcpy.SelectLayerByAttribute_management(sourcepoints,"NEW_SELECTION",strSQL2) #now select destination point in sourcepoints layer
                                arcpy.sa.CostPathAsPolyline(sourcepoints,costdist,"scratch/backlink","scratch/leastcostline.shp") #calculate least cost path from source to destination. 
                                with arcpy.da.SearchCursor("Scratch/leastcostline.shp","SHAPE@LENGTH") as cursor: #open least cost line and calculate length
                                    for line in cursor:
                                        leastcostdist.append(str(line[0])) #write length of least cost line to container variable
                                        arcpy.AddMessage("The least cost distance between point " + str(pf[0]) + " and point " + str(pt[0])+ " is " + str(line[0]))
                                del cursor
                #clean up cursors, reset layer selections, and write data to file. 
                sink.reset()
                euclideandist_final = ','.join(euclideandist)
                leastcostdist_final = ','.join(leastcostdist)
                f.write(euclideandist_final+"\n")
                g.write(leastcostdist_final+"\n")
            source.reset()
            arcpy.SelectLayerByAttribute_management(sourcepoints,"CLEAR_SELECTION")
            f.close()
            g.close()
            del source
            del sink
        else:
            os.chdir(path) #resert directory to home folder
            arcpy.AddMessage("Calculating outputs for interval "+ str(i))
            #setup search cursors for source and destination points
            source1 = arcpy.da.SearchCursor(sourcepoints,["FID","SHAPE@","SHAPE@X","SHAPE@Y"])
            sink1 = arcpy.da.SearchCursor(sourcepoints,["FID","SHAPE@","SHAPE@X","SHAPE@Y"])
            arcpy.MakeFeatureLayer_management(outpath+"/shapefile/interval"+str(i)+".shp",intervalshp)
            #open output files and write header 
            h = open(outpath+"/individual_leastcost_interval"+str(i)+".csv","w")
            h.write(header)
            inraster = arcpy.ASCIIToRaster_conversion(outpath+"/raster/interval"+str(i)+".asc") #convert cost raster into a readable format
            #inraster = Raster(inraster)
            arcpy.DefineProjection_management(inraster,outpath+"/raster/interval"+str(i)+".prj") #set projection of input raster
            for pf1 in source1: #start first order for loop for origin points
                leastcostdist = [str(pf[0])] #write source point FID as first value to container variable
                for pt1 in sink1:
                    if pf1 == pt1:
                        leastcostdist.append("NA")
                    else:
                        strSQL1 = """ "FID" = {0}""".format(pf1[0]) #define SQL search string for source point
                        strSQL2 = """ "FID" = {0}""".format(pt1[0]) #define SQL search string for destination point
                        arcpy.SelectLayerByAttribute_management(sourcepoints,"NEW_SELECTION",strSQL1) #select source point in sourcepoints shapefile 
                        arcpy.SelectLayerByLocation_management(intervalshp,"INTERSECT",sourcepoints, selection_type = "NEW_SELECTION") #using source point, select the overlapping polygon on the intervalshp shapefile
                        if int(arcpy.GetCount_management(intervalshp).getOutput(0)) < 1: #test to see if point is below sea level, write NA if true
                            arcpy.AddMessage("Point "+str(pf1[0])+" is below sea level during interval "+str(i)+", writing distance value of NA")
                            leastcostdist.append("NA")
                        else:
                            arcpy.SelectLayerByAttribute_management(sourcepoints,"ADD_TO_SELECTION",strSQL2) #if source point is on valid landmass, select destination point in sourcepoints shapefile
                            arcpy.SelectLayerByLocation_management(intervalshp,"INTERSECT",sourcepoints, selection_type = "ADD_TO_SELECTION") #select island polygon based on destination point
                            if int(arcpy.GetCount_management(intervalshp).getOutput(0)) == 1: #two possibilities here: either both points lie on the same island or the destination point is underwater
                                arcpy.SelectLayerByAttribute_management(sourcepoints,"NEW_SELECTION",strSQL2) #reselect destination point as a new selection
                                arcpy.SelectLayerByLocation_management(intervalshp,"INTERSECT",sourcepoints,selection_type = "REMOVE_FROM_SELECTION") #based on destination point, remove intersecting island polygon from selection
                                if int(arcpy.GetCount_management(intervalshp).getOutput(0))  == 1: #if there is no change to the number of selected polygons, then the destination point is underwater, write NA value.
                                    arcpy.AddMessage("Destination point "+str(pt1[0])+" is underwater, writing a distance value of NA")
                                    leastcostdist.append("NA")
                                else:
                                    arcpy.SelectLayerByAttribute_management(sourcepoints,"NEW_SELECTION",strSQL1) #reselect source point in sourcepoints layer 
                                    costdist = CostDistance(sourcepoints,inraster,"","Scratch/backlink") #generate cost distance raster for source point
                                    arcpy.SelectLayerByAttribute_management(sourcepoints,"NEW_SELECTION",strSQL2) #now select destination point in sourcepoints layer
                                    arcpy.sa.CostPathAsPolyline(sourcepoints,costdist,"Scratch/backlink","Scratch/leastcostline.shp")
                                    with arcpy.da.SearchCursor("Scratch/leastcostline.shp","SHAPE@LENGTH") as cursor:
                                        for line1 in cursor:
                                            leastcostdist.append(str(line1[0]))
                                            arcpy.AddMessage("The least cost distance between point " + str(pf1[0]) + " and point " + str(pt1[0])+ " is " + str(line1[0]))
                                    del cursor
                            else: #either the points are on the same island or on different islands
                                arcpy.SelectLayerByAttribute_management(sourcepoints,"NEW_SELECTION",strSQL1) #reselect source point in sourcepoints layer 
                                costdist = CostDistance(sourcepoints,inraster,"","Scratch/backlink") #generate cost distance raster for source point
                                arcpy.SelectLayerByAttribute_management(sourcepoints,"NEW_SELECTION",strSQL2) #now select destination point in sourcepoints layer
                                arcpy.sa.CostPathAsPolyline(sourcepoints,costdist,"Scratch/backlink","scratch/leastcostline.shp")
                                with arcpy.da.SearchCursor("Scratch/leastcostline.shp","SHAPE@LENGTH") as cursor:
                                    for line1 in cursor:
                                        leastcostdist.append(str(line1[0]))
                                        arcpy.AddMessage("The least cost distance between point " + str(pf1[0]) + " and point " + str(pt1[0])+ " is " + str(line1[0]))
                                del cursor
                leastcostdist_final = ','.join(leastcostdist) #format container variable into writable string
                h.write(leastcostdist_final+"\n") #write distances to output file
                sink1.reset() #reset cursor
            arcpy.SelectLayerByAttribute_management(sourcepoints,"CLEAR_SELECTION") #unselect all points for subsequent iterations
            h.close()
            source1.reset() #reset cursor
            del source1 #delete cursors to release memory
            del sink1
        shutil.rmtree("Scratch") #wipe scratch folder