import numpy as np
import pandas as pd
import os

#set working directory to current file directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))
#set current directory as path variable
path = os.getcwd()
inputpath = "examples/output/"
outpath = "examples/output/"

#create blank array for containing distance matrix file names
leastdistfiles = []
eucdistfiles = []

#load interval file
intervalfile = pd.read_csv(inputpath+'intervals.csv')
#extract list of intervals
intervals = intervalfile['Interval'].tolist()
#extract list of time durations for each interval, which will be used as the weights for averaging
weights = np.array(intervalfile['TimeInterval'].tolist())

#create list of distance matrices for least distance
for i in intervals:
    leastdistfiles.append("island_leastdist_interval{}.csv".format(i))
    eucdistfiles.append("islandcentroid_euclidean_interval{}.csv".format(i))

leastdist_dfs = [pd.read_csv(inputpath+f, header=0, index_col=0) for f in leastdistfiles]
eucdist_dfs = [pd.read_csv(inputpath+g, header=0, index_col=0) for g in eucdistfiles]
leastdist_df = pd.concat(leastdist_dfs).groupby(level=0)
eucdist_df = pd.concat(eucdist_dfs).groupby(level=0)

#open file for writing final weighted average distance matrix
f = open(outpath+"island_leastdist_averaged.csv","w")
g = open(outpath+"islandcentroid_euclidean_averaged.csv","w")

#print(df.get_group(0)[['1']])
#create array of number of points
points = range(0,len(leastdist_df))
#prepare header string and write to file
header = "FID,"+",".join(map(str,points))+"\n"
f.write(header)
g.write(header)
weights_reshaped = weights.reshape(len(leastdist_dfs),1)

#start iterating through interval matrices
for x in points:
    leastdistrow= [str(x)]
    eucdistrow = [str(x)]
    for y in points:
        leastdistarray = np.array(leastdist_df.get_group(x)[[str(y)]])
        leastdistmasked = np.ma.masked_array(leastdistarray,np.isnan(leastdistarray))
        leastdistavg = np.ma.average(leastdistmasked, axis = 0, weights=weights)
        leastdistrow.append(str(float(leastdistavg)))
        eucdistarray = np.array(eucdist_df.get_group(x)[[str(y)]])
        eucdistmasked = np.ma.masked_array(eucdistarray,np.isnan(eucdistarray))
        eucdistavg = np.ma.average(eucdistmasked,axis=0,weights=weights)
        eucdistrow.append(str(float(eucdistavg)))
    leastdist = ','.join(leastdistrow)
    eucdist = ','.join(eucdistrow)
    f.write(leastdist+"\n")
    g.write(eucdist+"\n")
f.close()
g.close()

# distarray = np.array(df.get_group(0)[['7']])
# masked = np.ma.masked_array(distarray,np.isnan(distarray))
# avg = np.ma.average(masked, axis = 0, weights=weights)
# print(avg)