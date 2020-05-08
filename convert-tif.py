# conda create --name terrafusion-cog python=3.7; cd terrafusion-cog
# source bin/activate
# pip install fsspec h5py s3fs

# Install gdal
# conda install gdal s3fs rio-cogeo
import s3fs
import h5py
from osgeo import osr, gdal
import numpy as np

filelocation = 'terrafusiondatasampler/P233/TERRA_BF_L1B_O73748_20131029135319_F000_V001.h5'
s3 = s3fs.S3FileSystem()
hdfFile = s3.open(f"s3://{filelocation}", 'rb')
f = h5py.File(hdfFile)

granule = 'granule_2013302_1425'
ev_data = np.array(f[f"//MODIS/{granule}/_1KM/Data_Fields/EV_1KM_Emissive"][:])
lat = np.array(f[f"//MODIS/{granule}/_1KM/Geolocation/Latitude"][:])
lon = np.array(f[f"//MODIS/{granule}/_1KM/Geolocation/Longitude"][:])

xmin, ymin, xmax, ymax = [lon.min(), lat.min(), lon.max(), lat.max()]
nrows,ncols = np.shape(lon)
xres = (xmax-xmin) / float(ncols)
yres = (ymax-ymin) / float(nrows)
geotransform = (xmin, xres, 0, ymax, 0, -yres) 

output_raster = gdal.GetDriverByName('GTiff').Create('test.tif', ncols, nrows, 1, gdal.GDT_Float64)  # Open the file
output_raster.SetGeoTransform(geotransform)
output_raster.GetRasterBand(1).WriteArray(data_to_write)
output_raster.GetRasterBand(1).SetNoDataValue(-999)
srs = osr.SpatialReference()                 # Establish its coordinate encoding
srs.ImportFromEPSG(4326)                     # This one specifies WGS84 lat long.
output_raster.SetProjection( srs.ExportToWkt() )   # Exports the coordinate system 

output_raster.FlushCache()
output_raster = None
# rio cogeo create test.tif test.cog.tif
