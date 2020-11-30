# PleistoDist
Distance matrices between islands normalised over Pleistocene time

[Last updated: 29 Nov 2020]

## Introduction

PleistoDist is a tool for visualising and quantifying the effects of Pleistocene-era sea level change on islands over time. This tool consists of a series of Python scripts that utilise standard ArcPy functions to generate maps of island extents for different Pleistocene-era sea levels, and calculate the mean inter-island distance normalised over time. 

## Requirements

As this package requires ArcPy to function, users need to have the following dependencies installed in order to use PleistoDist:
* Python 2.7.x
* ArcMap 10.6 (or later)

Because this package was originally designed as an ArcGIS toolbox, it only runs on Windows machines. If there is sufficient demand, I will rewrite this package for cross-platform use, possibly as a QGIS plugin or as an R package. 

## Usage

This package can be run either as an ArcGIS toolbox or as a standalone Python script. The ArcGIS toolbox version can be run in ArcMap or ArcCatalog and comes with a small graphical user interface (GUI), but runs a little bit slower than the standalone Python script, so I would advise using the ArcGIS toolbox interface only for smaller runs (with fewer source points and/or fewer intervals). 

### Inputs

You will need the following inputs in order to run PleistoDist:
* **Bathymetry raster** [.ASC] : PleistoDist requires an input bathymetry raster file in ASCII (.ASC) format to generate its outputs. Although PleistoDist should theoretically be able to use any type of ASCII-formatted bathymetric map as input, this tool has been tested specifically with data from the General Bathymetric Chart of the Oceans (GEBCO: https://www.gebco.net). Locality-specific bathymetric maps can be downloaded from https://download.gebco.net/. The example dataset contains a bathymetric raster of the Fijian archipelago. 
* **Source points** [.SHP]: You will need to prepare a shapefile (.SHP format) of reference points that PleistoDist will use as sampling localities to calculate inter-island distance matrices. The shapefile can be formatted in any map projection, since PleistoDist will reproject the shapefile to the user-specified projection for this analysis (see next point). Note, however, that the reprojection process might result in points close to the shoreline ending up in the sea, so do be mindful of that.  
* **Map projection** [EPSG code]: Because of the Earth's spherical shape, we need to apply a map projection to accurately calculate straight-line distances between points. Users should specify a projected coordinate system appropriate to the area being analysed using the projection's associated EPSG code (https://epsg.org/home.html). Geographic coordinate system projections are not recommended as those will result in distance matrices calculated in decimal degrees rather than distance units. In the example dataset, we use the EPSG 3141 projection (Fiji 1956 / UTM zone 60S) for the islands of Fiji. 
* **Time cutoff** [kya]: PleistoDist calculates the average distance between islands over a specific period of time. Users will have to specify an upper time bound (in thousands of years [kya]) for their PleistoDist analysis, which can range from 0.1 kya to 3000 kya (i.e. 100 to 3,000,000 years ago). The lower time bound is fixed at the present day (0 kya). See the "How it works" section of the README file for more details. 
* **Binning Mode and number of intervals**: PleistoDist simplifies the distance over time calculation by binning either time or sea levels into a number of equal user-specified intervals. This allows users to specify the coarseness of their analysis, with more intervals resulting in a more accurate and finer-grained analysis, although that will generate more output files and require a longer computational time. Binning by time is recommended for beginner users since it is more intuitive and more accurate as well. See the "How it works" section of the README file for more information on the difference between binning by time or by sea level. 

### Using the standalone Python script

After downloading the PleistoDist repository, the standalone Python script can be run using the command 

```python pleistodist.py```

This calls the ```pleistodist.py``` wrapper script, which prompts users for the relevant input and runs the entire pipeline. All input files (bathymetry raster and source points) should be placed in the **input** folder, and PleistoDist outputs (interval file, map files, and distance matrices) will be generated in the **output** folder. Remember to remove data from prior runs from the output folder before starting a new PleistoDist run, and remember not to delete the output folder or its folder substructure. 

### Using the ArcGIS toolbox

The PleistoDist ArcGIS toolbox can be found in the ```PleistoDist_arcmaptoolbox``` folder. You can run the toolbox by loading the ```PleistoDist.tbx``` file into ArcMap or ArcCatalog. The toolbox currently provides two running modes:
* **PleistoDist** runs the entire PleistoDist pipeline from map generation to distance matrix calculation.
* **Generate Sea Level Maps** runs a subsection of the pipeline that generates only sea level maps and skips the time-consuming process of calculating inter-island distance matrices. 

## How it works

PleistoDist works by simplifying Pleistocene-era sea level change into discrete intervals, calculating inter-island distances for each interval, and performing a weighted average of inter-island distance across all intervals. This section provides a brief overview of each of the modules contained within PleistoDist, and how mean inter-island distance over time is calculated. 

* **getintervals.py**: The main role of the ```getintervals.py``` and the related ```getintervals_sealvl.py``` modules are to simplify reconstructed Pleistocene sea levels (by default from Bintanja and van de Wal, 2008) into a series of discrete interval bins. These intervals can be calculated in two different ways: either by discretising time, or by discretising sea level, as is illustrated in Figure 1. Theoretically, both methods should be equally accurate when the number of intervals is very high, but for intermediate numbers of intervals, binning by time is likely to be a better measure since it samples only one continuous section of the sea level curve per interval, and thus makes fewer assumptions about the shape of the curve for each interval. However, whether to bin intervals by time or sea level will likely vary depending on spatial and temporal scale, as well as the spatial context of the analysis, and as such both binning modes are made available in PleistoDist. The results of the binning process will be saved as an **interval file** in the output folder (see Figure 1), which will be used by subsequent modules for generating map outputs and calculating distance matrices. Each row in the **interval file** corresponds to one interval, and the first interval is always set at present day, with a mean sea level of 0 m and a time interval of 0.1 kya. 

![alt text](https://github.com/g33k5p34k/PleistoDist/blob/main/images/Figure1.png "Figure 1")
**Figure 1**: PleistoDist provides two different methods for discretising sea level change, either by time (A) or by sea level (B). Both methods should yield similar results when the number of intervals is very high, but will differ significantly for lower numbers of intervals. As this figure suggests, for a time cutoff of 200,000 years, 2 intervals not enough to capture the true variability of sea level change over this time period. The results of the binning process will be written as a table to the interval file in the output folder. 

* **makerasters.py**: The ```makerasters.py``` module is responsible for generating map outputs based on the interval bins contained in the **interval file**. This module reprojects the input bathymetry raster into the user specified map projection using a bilinear resampling method, and generates a raster and shapefile of land extents based on the mean sea levels specified in the MeanDepth column of the **interval file**. The output rasters and shapefiles are saved in their respective folders in the output folder. 

* **islandmode.py**: The ```islandmode.py``` module is a fairly long and complex script that generates two types of distance matrices between islands: the least shore-to-shore distance and the centroid-to-centroid distance (see Figure 2). For each pairwise combination of source points provided by the user, ```islandmode.py```  selects the landmasses corresponding to the pair of points, and calculates the two distance measures between the landmasses. If both points are on the same island for that particular interval, a distance of 0 is returned. And if one or both points are underwater during that particular interval, a value of NA is returned. Distance matrix outputs from this module are stored in the output folder. 

![alt text](https://github.com/g33k5p34k/PleistoDist/blob/main/images/Figure2.png "Figure 2")
**Figure 2**: PleistoDist calculates two different distance measures between islands: the least shore-to-shore distance, and the centroid-to-centroid distance, illustrated here with the Fijian islands of Vanua Levu, Taveuni, and Koro.  

* **calcmatrices.py**: Finally, the ```calcmatrices.py``` module calculates the average inter-island distance based on the distance matrices generated by ```islandmode.py```, weighted by the time duration of each interval (from the timeinterval column in the interval file). 

## Limitations

PleistoDist assumes that the bathymetry of the area of interest is constant throughout the time period being modelled. This is an important assumption to bear in mind since bathymetry can be affected by tectonic and volcanic activity. In the provided example of the Fijian archipelago, for instance, the island of Taveuni is likely to have emerged around 700,000 years ago, so analyses with a cutoff time exceeding 700 kya are unlikely to be accurate. In addition, PleistoDist is unable to account for the effect of proximate ice sheets on the bathymetry and sea level of the area of interest, and is thus likely to be less accurate at very high or very low latitudes. It is also possible that the default global sea level reconstruction used in the vanilla version of PleistoDist may not be accurate for particular areas of interest, in which case users are advised to replace the ```sealvl.csv``` file contained in the input folder with their preferred sea level reconstruction, bearing in mind to be aware of the column names in the ```sealvl.csv``` file. 

### Further modifications/extensions

Advanced users should be able to modify the PleistoDist source code to meet their specific needs. Here are some suggestions:
* **Sea level reconstruction**: By default, PleistoDist uses the Pleistocene sea level reconstruction of Bintanja & van de Wal (2008), which is based on an inverse model using the ratio of marine Oxygen-18 to Oxygen-16 isotopes. This sea level reconstruction is stored as a CSV file in the input folder (for the standalone Python script) and the ToolData folder (for the ArcGIS toolbox), and can be replaced with your preferred sea level reconstruction. If you do swap out the ```sealvl.csv``` file, be sure to check and modify the ```getintervals.py``` file to make sure that this doesn't break PleistoDist. 
* **Time lower bound**: Vanilla PleistoDist fixes the lower time bound at the present day. Setting a different lower time bound should be relatively simple and can be achieved by modifying the ```getintervals.py``` file. 

