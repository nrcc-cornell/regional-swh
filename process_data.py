import numpy as np
import xarray as xr
import datetime as datetime
import json
from shapely.geometry import Point, Polygon
import pathlib

import config




def construct_output_path(orig_name, output_type, output_dir):
  if output_type == 'csv' or output_type == 'json':
    file_ext = '.' + config.output_type
  else:
    file_ext = '.csv'

  new_name = orig_name
  counter = 0
  while output_dir.joinpath(new_name + file_ext).exists():
    counter += 1
    new_name = f'{orig_name}({counter})'
  return output_dir.joinpath(new_name + file_ext)

def process_data(data_type):
  # Set parameters. Region of interest corresponds to the shapefile (opened later)
  if data_type == 'wave':
    thres = config.wave_thres
    temporal_thres = config.wave_temporal_thres
    intervene = config.wave_intervene
    spatial_t = config.wave_spatial_t
    data_file_base_name = config.wave_data_base_name
  elif data_type == 'storm':
    thres = config.storm_thres
    temporal_thres = config.storm_temporal_thres
    intervene = config.storm_intervene
    spatial_t = config.storm_spatial_t
    data_file_base_name = config.storm_data_base_name

  code_path = pathlib.Path(__file__).parent
  if config.data_dir == 'default':
    data_dir = code_path.joinpath('data')
  else:
    data_dir = config.data_dir

  if config.geojson_file == 'default':
    geojson_file = code_path.joinpath('geojson', 'NES_5REGIONS.json')
  else:
    geojson_file = config.geojson_file

  if config.output_dir == 'default':
    output_dir = code_path.joinpath('results')
  else:
    output_dir = config.output_dir

  output_path = construct_output_path(f'{data_type}_{config.start_year}-{config.end_year}', config.output_type, output_dir)

  start_date = datetime.datetime(config.start_year, 1, 1, 0)

  # Establish a list of years, beginning at start year
  key_year = np.arange(config.start_year, config.end_year + 1).tolist()

  # Create list of accessible data files in year range
  df = []
  for yr in range(config.start_year, config.end_year + 1):
    infile_name = data_dir.joinpath(f'{data_file_base_name}{str(yr)}.nc')
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

  if config.output_type == 'csv':
    file_data = [','.join(['region', *[str(yr) for yr in key_year]])]
  elif config.output_type == 'json':
    file_data = {}

  for reg_of_int in config.regs_of_int:
    print(f'  Working on region {reg_of_int}')
    
    # select a region of interest, as input by setting the parameters
    in_region = region_num == reg_of_int

    if data_type == 'wave':
      # extract wave values for entire era5 domain
      raw = ds.swh
    elif data_type == 'storm':
      # convert wind speed from m/s (as provided by era5) to knots
      raw = np.sqrt((ds.u10*1.94384)**2+(ds.v10*1.94384)**2)
    
    # extract wind speed values for entire era5 domain
    reg_vals = raw.values

    # Index wave values for the entire era5 domain by the region of interest
    region = reg_vals[:, in_region]

    # Count the number of data points in the dataset and find the proportion of wave values meeting the #threshold at each hour
    time = raw.time
    r_t = time.values
    point_count = region.shape[1]
    points = np.arange(0, point_count)

    sp = []
    for i in range(0, len(time)):
      v = np.where(region[i]>= thres, 1, 0)
      x = v.sum()/point_count
      sp.append(x)

    g = np.array(sp)
    gale = np.where(g>=spatial_t, 1, 0).tolist()



    ## DURATION

    if data_type == 'wave': gale[0] = 0

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
    
    if config.output_type == 'csv':
      new_row = [f'region {reg_of_int}']
      for tup in c:
        new_row.append(str(tup[1]))
      file_data.append(','.join(new_row))
    elif config.output_type == 'json':
      file_data[f'region {reg_of_int}'] = counts

  if config.output_type == 'csv':
    with open(output_path, 'w') as f:
      for row in file_data:
        f.write(row + '\n')
  elif config.output_type == 'json':
    with open(output_path, 'w') as f:
      json.dump(file_data, f, indent=2)
