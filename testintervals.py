import os
import math
import numpy
import pandas
from getintervals import getintervals_time
from getintervals_sealvl import getintervals_sealvl
from makerasters import makerasters

sealvl = pandas.read_csv('input/sealvl.csv')
time = 10
intervals = 10
getintervals_time(sealvl, time, intervals)
makerasters("output/intervals.csv","FJ.asc","3141")
