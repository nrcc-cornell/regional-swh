import numpy as np
import xarray as xr
import datetime as datetime
import json
from shapely.geometry import Point, Polygon
import pathlib


#######################################################################################
# Adjust these as needed. Years in range that do not have a data file will be skipped #
#######################################################################################
start_yr = 2000
end_yr = 2002
#######################################################################################


# Set parameters. Region of interest corresponds to the shapefile (opened later)
base_path = pathlib.Path(__file__).parent.parent
data_dir = base_path.joinpath('data')
geojson_file = base_path.joinpath('geojson', 'NES_5REGIONS.json')
start_date = datetime.datetime(start_yr, 1, 1, 0)

# Establish a list of years, beginning at start year
key_year = np.arange(start_yr, end_yr).tolist()

# Region of interest (0 = dark blue region, 1 = light blue, 2 = green, 3 = yellow , 4 = red)
reg_of_int = 4

# Wave threshold, in meters
wave_t = 5

# Duration threshold, in hours
temporal_thres = 3

# time between one event’s start and a previous event in hours
intervene = 96

# Wind speed spatial threshold, as a proportion of the grids
spatial_t = .25

# Create list of accessible data files in year range
dfwav = []
for yr in range(start_yr,end_yr):
  infile_name_wav = data_dir.joinpath(f'Atlantic_waves_{str(yr)}.nc')
  if infile_name_wav.exists(): dfwav.append(infile_name_wav)

# Open shapefile provided by Kim Hyde
f = open(geojson_file)
data = json.load(f)

# Open .nc dataset. This command links each year’s .nc file year to year
dsw = xr.open_mfdataset(dfwav)

# Pull out longitude and latitude
lonw = dsw.longitude
latw = dsw.latitude

# length of each lon and lat arrays
len_lonw = len(lonw)
len_latw = len(latw)

# this code defines a np.array that converts points in the era5 data domain to each corresponding region
region_numw = np.full((len_latw, len_lonw), np.nan)
for ln in range(0, len_lonw):
  for lt in range(0, (len_latw)):
    era5_point = Point(float(lonw[ln]), float(latw[lt]))

    for i in range(0,5):
      region_point = Polygon(data['features'][i]['geometry']['coordinates'][0])
      ir = era5_point.intersects(region_point)

      if ir:
        region_numw[lt][ln] = i
        break

# select a region of interest, as input by setting the parameters
in_regionw = region_numw == reg_of_int

# extract wave values for entire era5 domain
wav = dsw.swh
wav_val = wav.values

# Index wave values for the entire era5 domain by the region of interest
region_wav = wav_val[:, in_regionw]

# Count the number of data points in the dataset and find the proportion of wave values meeting the #threshold at each hour
wav_time = wav.time
w_t = wav_time.values
point_count = region_wav.shape[1]
points = np.arange(0, point_count)

spw = []
for i in range(0, len(wav_time)):
  v = np.where(region_wav[i]>= wave_t, 1, 0)
  x = v.sum()/point_count
  spw.append(x)

gw = np.array(spw)
gale = np.where(gw>=spatial_t, 1, 0).tolist()



## DURATION

gale[0] = 0

# Calculate the difference between one hour and the next hour. A 1 corresponds to the first #index of a wave event, and a -1 corresponds to the index after a wave event has ended. This #array has one less index than actual counts of wave events, however this is later corrected
gale_dura = np.diff(gale)

# Locate the indices where a wave event starts, adding to ensure proper shape
gale_start = np.argwhere(gale_dura == 1)+1

#Locate the indices where a gale ends, adding a 1 to ensure proper shape
gale_end = np.argwhere(gale_dura == -1)+1

# Find the duration of each event by subtracting the start index from the end index
duration = gale_end-gale_start

# Count the number of events where the duration is larger than or equal to 3
gale_event_3hr = np.count_nonzero(duration >=temporal_thres)
index_3hr = np.where(duration>=3)
gale_3hrs = [start_date+datetime.timedelta(hours = int(gale_start[index_3hr][i])) for i in range(0, len(index_3hr[0]))]

# Concatenate the index of the start of a gale event and its duration into one 2X1 numpy array
gale_start_duration = np.concatenate([(gale_start), (duration)], axis = 1)

# Filter out events that do not last longer than the temporal or duration threshold
gale_duration = gale_start_duration[np.all(gale_start_duration>=temporal_thres, axis = 1)]



## INTERVENING PERIOD

# This ensures that an event beginning less than 96 hours after the dataset begins is counted
gale[0] = 1

# Finding the hours in which a wave event is occurring, or in other words where a 1 occurs in #gale_hour_counter
gale_index = np.array(np.where(np.array(gale) == 1))

# Calculate the difference between each successive index, each corresponding to an hour that #meets the wave threshold conditions, in order to find how many hours pass between the last #hour of one event and the first hour of the next event.
# NOTE: the difference has one less index than the total amount of indexes experiencing a wave event.
gale_diff = np.array(np.diff(gale_index))

# Find where the difference between the end of one event and the start of another event is #greater than or equal to 96 (96 hours or 4 days between events)
gale_interv = np.where(gale_diff>=intervene)[1]+1

# Count the beginning of wave events that are spaced by 96 indices (96 hours) from the #previous first hour of a gale event
gale_event_96hr = np.count_nonzero(gale_interv)

#index = [gale_index[0][gale_interv[1][i]] for i in range(0, len(gale_interv[1]))]

# find the hours as a datetime object a wave event begins and is 96 hours after the start of a #previous gale event.
gale_times_interv = [start_date + datetime.timedelta(hours = int(gale_index[0][gale_interv[i]])) for i in range(0, len(gale_interv))]

# Find the starting hour for a wave event that is both 3 hours long, and is 96 hours after the #starting hour for a previous event using if/else statement
GALE = np.intersect1d(gale_times_interv, gale_3hrs)

# Print a time series of annual event counts. Each index corresponds to a year in key_year
plot = [GALE[i].year for i in range(0,len(GALE))]
counts = {k: plot.count(k) for k in key_year}
c = sorted(counts.items())
plot = []

for i in range(0, len(c)):
  z = c[i][1]
  plot.append(z)

print(plot)