import pandas
import os
import numpy

def getintervals_sealvl (sealvl,time,intervals):
#subset full sea level table based on cutoff time
    sealvl_subset = sealvl[(sealvl.Time <= time) & (sealvl.Time > 0)] #since T = 0 is a special case, ignore the first row where T = 0
    print(sealvl_subset[['Time','Sealevel_Uncorrected','Sealevel_Corrected']])
    #calculate range of sea level depth values 
    rangemax = max(sealvl_subset.Sealevel_Corrected[1:])
    rangemin = min(sealvl_subset.Sealevel_Corrected[1:])

    depthinterval = rangemin / intervals

    #create empty text file
    f = open(r"output/intervals.csv","w")
    #write file headers
    f.write("Interval,MinDepth,MaxDepth,MeanDepth,TimeInterval\n")
    f.write("0,0,0,0,1\n") #set present day sea levels as the first time interval
    #the big nested loop function that calculates the sea level interval bounds and the timespan of each interval
    for x in range(1,intervals+1,1):
        if x == 1: #since the first interval has a fixed lower bound, calculate first  interval separately
            #since each line in the input sea level file corresponds with 0.1 kya, timespan can be calculated by counting number of valid rows
            timeinterval = len(sealvl_subset[(sealvl_subset.Sealevel_Corrected <= rangemax) & (sealvl_subset.Sealevel_Corrected >= depthinterval)])
            #calculate lowest sea level depth within interval
            mindepth = max(sealvl_subset[(sealvl_subset.Sealevel_Corrected <= rangemax) & (sealvl_subset.Sealevel_Corrected >= depthinterval)].Sealevel_Corrected)
            #calculate greatest sea level depth within interval
            maxdepth = min(sealvl_subset[(sealvl_subset.Sealevel_Corrected <= rangemax) & (sealvl_subset.Sealevel_Corrected >= depthinterval)].Sealevel_Corrected)
            #find the mean sea level depth based on minimum and maximum
            meandepth = (mindepth + maxdepth) / 2
        else: #for every interval > 1, calculate interval range, mean, and timespan
            timeinterval = len(sealvl_subset[(sealvl_subset.Sealevel_Corrected < depthinterval*(x-1)) & (sealvl_subset.Sealevel_Corrected >= depthinterval*x)])
            mindepth = max(sealvl_subset[(sealvl_subset.Sealevel_Corrected < depthinterval*(x-1)) & (sealvl_subset.Sealevel_Corrected >= depthinterval*x)].Sealevel_Corrected)
            maxdepth = min(sealvl_subset[(sealvl_subset.Sealevel_Corrected < depthinterval*(x-1)) & (sealvl_subset.Sealevel_Corrected >= depthinterval*x)].Sealevel_Corrected)
            meandepth = (mindepth + maxdepth) / 2
        #concatenate outputs into a single line
        output = str(x) + "," + str(mindepth) + "," + str(maxdepth) + "," + str(meandepth) + "," + str(timeinterval) + "\n"
        #write outputs
        f.write(output)
    f.close()