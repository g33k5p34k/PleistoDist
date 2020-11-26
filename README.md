# PleistoDist
Distance matrices between islands normalised over Pleistocene time

[Last updated: 26 Nov 2020]

## Introduction

PleistoDist is a tool for visualising and quantifying the effects of Pleistocene-era sea level change on islands over time. This tool consists of a series of Python scripts that utilise standard ArcPy functions to generate maps of island extents for different Pleistocene-era sea levels, and calculate the mean inter-island distance normalised over time. 

## Requirements

As this package requires ArcPy to function, users need to have the following dependencies installed in order to use PleistoDist:
* Python 2.x (preferably Python 2.7.x)
* ArcMap 10.6

Because this package was originally designed as an ArcGIS toolbox, it only runs on Windows machines. If there is sufficient demand, I will rewrite this package for cross-platform use, possibly as a QGIS plugin or as an R package. 

## Usage Instructions

This package can be run either as an ArcGIS toolbox or as a standalone Python script. The ArcGIS toolbox version can be run in ArcMap or ArcCatalog and comes with a small graphical user interface (GUI), but runs a little bit slower than the standalone Python script, so I would advise using the ArcGIS toolbox interface only for smaller runs (with fewer source points and/or fewer sea level intervals). 

### Inputs

You will need the following inputs in order to run PleistoDist:
* **Bathymetry raster** [.ASC] : PleistoDist requires an input bathymetry raster file in ASCII (.ASC) format to generate its outputs. Although PleistoDist should theoretically be able to use any type of ASCII-formatted bathymetric map as input, this tool has been tested specifically with data from the General Bathymetric Chart of the Oceans (GEBCO: https://www.gebco.net). Locality-specific bathymetric maps can be downloaded from https://download.gebco.net/. The example dataset contains a bathymetric raster of the Fijian archipelago. 
* **Source points** [.SHP]: You will need to prepare a shapefile (.SHP format) of reference points that PleistoDist will use as sampling localities to calculate inter-island distance matrices. The shapefile can be formatted in any map projection, since PleistoDist will reproject the shapefile to the user-specified projection for this analysis (see next point). Note, however, that the reprojection process might result in points close to the shoreline ending up in the sea, so do be mindful of that.  
* **Map projection** [EPSG code]: Because of the Earth's spherical shape, we need to apply a map projection to accurately calculate straight-line distances between points. Users should specify a projected coordinate system appropriate to the area being analysed using the projection's associated EPSG code (https://epsg.org/home.html). Geographic coordinate system projections are not recommended as those will result in distance matrices calculated in decimal degrees rather than distance units. In the example dataset, we use the EPSG 3141 projection (Fiji 1956 / UTM zone 60S) for the islands of Fiji. 
* **Time cutoff** [kya]: PleistoDist calculates the average distance between islands over a specific period of time. Users will have to specify an upper time bound (in thousands of years [kya]) for their PleistoDist analysis, which can range from 0.1 kya to 3000 kya (i.e. 100 to 3,000,000 years ago). The lower time bound is fixed at the present day (0 kya). See the "How it works" section of the README file for more details. 
* **Number of sea level intervals**: PleistoDist simplifies the sea level calculation by binning the total change in sea level for the user-specified time duration into a number of equal intervals. This allows users to specify the coarseness of their analysis, with more intervals resulting in a finer-grained analysis, although that will generate more output files and require a longer computational time. 

### ArcGIS Toolbox



### Further modifications

Advanced users should be able to customise PleistoDist to meet their specific needs. Here are some suggestions:
* **Sea level reconstruction**: By default, PleistoDist uses the Pleistocene sea level reconstruction of Bintanja & van de Wal (2008), which is based on an inverse model using the ratio of marine Oxygen-18 to Oxygen-16 isotopes. This sea level reconstruction is stored as a CSV file in the input folder (for the standalone Python script) and the ToolData folder (for the ArcGIS toolbox), and can be replaced with your preferred sea level reconstruction. If you do swap out the sealvl.csv file, be sure to check the getintervals.py file to make sure that this doesn't break PleistoDist. 
* **Time lower bound**: Vanilla PleistoDist fixes the lower time bound at the present day. Setting a different lower time bound should be relatively simple and can be achieved by modifying the getintervals.py file. 

## How it works

Lorem ipsum dolor sit amet
