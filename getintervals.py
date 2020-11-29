import os 
import math
import pandas
import numpy

def getintervals_time (sealvl,time,intervals):
    print("Preparing interval file... ")
    #subset full sea level table based on cutoff time
    sealvl_subset = sealvl[(sealvl.Time <= time) & (sealvl.Time > 0)] #since T = 0 is a special case, ignore the first row where T = 0
    sealvl_subset = sealvl_subset[['Time','Sealevel_Corrected']]
    #calculate time interval
    timeinterval = time/intervals
    #create empty text file
    f = open(r"output/intervals.csv","w")
    #write file headers
    f.write("Interval,MinDepth,MaxDepth,MeanDepth,LowerTimeBound,UpperTimeBound,TimeInterval\n")
    f.write("0,0,0,0,0,0,0.1\n") #set present day sea levels as the first time interval
    #set interval range (excluding interval 0)
    intvrange = range(1,intervals+1,1)
    for x in intvrange:
        #subset sea level table for specific time interval
        intvl = sealvl_subset[(sealvl_subset.Time > timeinterval*(x-1)) & (sealvl_subset.Time <= timeinterval*x)]
        #calculate sea level depth statistics
        mindepth = max(intvl.Sealevel_Corrected)
        maxdepth = min(intvl.Sealevel_Corrected)
        meandepth = numpy.mean(intvl.Sealevel_Corrected)
        #calculate time interval statistics
        lowertimebound = min(intvl.Time)
        uppertimebound = max(intvl.Time)
        timeduration = len(intvl.Time)*0.1
        #prepare output string and write to file
        output = str(x) + "," + str(mindepth) + "," + str(maxdepth) + "," + str(meandepth) + "," + str(lowertimebound) + "," + str(uppertimebound) + "," + str(timeduration) + "\n"
        f.write(output)
    f.close()