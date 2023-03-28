import numpy as np
import xarray as xr
import datetime as datetime
import json
from shapely.geometry import Point, Polygon
import pathlib


#######################################################################################
# Adjust these as needed. Years in range that do not have a data file will be skipped #
#######################################################################################
start_yr = 1998
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
reg_of_int = 0

# Wind threshold, in knots
gale_thres = 34

# Duration threshold, in hours
temporal_thres = 3

# time between one events start and a previous event in hours
intervene = 96

# Wind speed spatial threshold, as a proportion of the grids
st = .25

# Read in data from start year to end year, and store it as a list of .nc files (one index per each year)
df = []
for yr in range(start_yr,end_yr):
  infile_name = data_dir.joinpath(f'Atlantic_stormy_{str(yr)}.nc')
  if infile_name.exists(): df.append(infile_name)

# Open shapefile provided by Kim Hyde
f = open(geojson_file)
data = json.load(f)

# Open .nc dataset. This command links each year’s .nc file year to year
ds = xr.open_mfdataset(df)

# Pull out longitude and latitude
lon = ds.longitude
lat = ds.latitude

# length of each lon and lat arrays
len_lon = len(lon)
len_lat = len(lat)

# this code defines a np.array that converts points in the era5 data domain to each corresponding region
region_num = np.full((len_lat, len_lon), np.nan)
for ln in range(0, len_lon):
  for lt in range(0, (len_lat)):
    era5_point = Point(float(lon[ln]), float(lat[lt]))

    for i in range(0,5):
      region_point = Polygon(data['features'][i]['geometry']['coordinates'][0])
      ir = era5_point.intersects(region_point)

      if ir:
        region_num[lt][ln] = i
        break

# select region of interest, as input by setting the parameters
in_region = region_num == reg_of_int

# convert wind speed from m/s (as provided by era5) to knots
wisp = np.sqrt((ds.u10*1.94384)**2+(ds.v10*1.94384)**2)

# extract wind speed values for entire era5 domain
wisp_winds = wisp.values

# Index wind speed values for entire era5 domain by the region of interest
region_wind = wisp_winds[:, in_region]

# Count the number of data points in the dataset find the proportion of wind speed values meeting threshold at each hour
wisp_time = wisp.time
wsp_t = wisp_time.values
point_count = region_wind.shape[1]
points = np.arange(0, point_count)

# Create a list of 0s and 1s for each hour matching a certain speed threshold for a proportion of the grids
sp = []
for i in range(0, len(wisp_time)):
  # find for each hour meeting a wind speed threshold set in parameters
  v = np.where(region_wind[i]>= gale_thres, 1, 0)

  # Count the number of points > ws threshold in a single hour and divide by the total number of grid points
  x = v.sum()/point_count
  sp.append(x)

g = np.array(sp)

# Here is the list of 0s and 1s
gale = np.where(g>=st, 1, 0).tolist()



## DURATION

# Calculate the difference between one hour and the next hour. A 1 corresponds to the first index of a gale event, 
#and a -1 corresponds to the index after a gale has ended. This array has one less index than actual counts of gale, 
#however this is later corrected
gale_dura = np.diff(gale)

# Locate the indices where a gale starts, add 1 to ensure proper shape
gale_start = np.argwhere(gale_dura == 1)+1

#Locate the indicies where a gale ends, add 1 to ensure proper shape
gale_end = np.argwhere(gale_dura == -1)+1

# Find the duration of each event by subtracting the start index from the end index
duration = gale_end-gale_start

# Count the amount of events where the duration is larger than or equal to 3
gale_event_3hr = np.count_nonzero(duration >=temporal_thres)

# Find the indices where the duration meets the duration threshold set in parameters
index_3hr = np.where(duration>=temporal_thres)

# Find the index each event 3 or more hour long event begins
gale_3hrs = [start_date+datetime.timedelta(hours = int(gale_start[index_3hr][i])) for i in range(0, len(index_3hr[0]))]

# Concatenate the index of the start of a gale event and its duration into one 2X1 numpy array
gale_start_duration = np.concatenate([(gale_start), (duration)], axis = 1)

# Filter out events that do not last longer than the temporal or duration threshold
gale_duration = gale_start_duration[np.all(gale_start_duration>=temporal_thres, axis = 1)]



## INTERVENING PERIOD 

# This ensures that an event beginning less than 96 hours after the dataset begins is counted
gale[0] = 1

# Finding the hours in which a gale event is occurring, or in other words where a 1 occurs in gale_hour_counter
gale_index = np.array(np.where(np.array(gale) == 1))

# Calculate the difference between each successive index, each corresponding to an hour that experiences gale wind conditions, in order to find how many hours pass between the last hour of one event and the first hour of the next event.
# NOTE: the difference has one less index than the total number of indexes experiencing gale.
gale_diff = np.array(np.diff(gale_index))

# Find where the difference between the end of one event and the start of another event is greater than or equal to 96 
#       (96 hours or 4 days between events)
gale_interv = np.where(gale_diff>=intervene)[1]+1

# Count the beginning of a gale events that are spaced by 96 indices (96 hours) from the previous first hour of a 
#       gale event
gale_event_96hr = np.count_nonzero(gale_interv)

#index = [gale_index[0][gale_interv[1][i]] for i in range(0, len(gale_interv[1]))]

# find the hours as a datetime object a gale event begins and is 96 hours after the start of a previous gale event.
gale_times_interv = [start_date + datetime.timedelta(hours = int(gale_index[0][gale_interv[i]])) for i in range(0, len(gale_interv))]


# Find the starting hour for a gale event that is both 3 hours long and is 96 hours after the starting hour for a 
#       previous event 
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