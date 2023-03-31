#######################
### GENERAL OPTIONS ###
#######################

# Control the years that will be processed.
# end_year is included in output
# For single year make them both the same year
start_year = 1959
end_year = 2022

# 'both' runs for both wave and storm data
# 'storm' runs only storm data
# 'wave' runs only storm data
data_type = 'both'

# Controls whether to fetch data or not
# If there is already a data file to use, year will be skipped
#############################################################################
### WARNING: ################################################################
#############################################################################
###   Fetching data is a time consuming process! It could take many       ###
###   hours to fetch all necessary data. The data files are also large so ###
###   make sure you have the hard drive space to accomodate them          ###
###   wave = ~90MB/year    storm = ~860MB/year                            ###
#############################################################################
fetch_data = True

# Controls wheter to process the data or not
# Can be set to False if you are only looking to fetch new data
# When processing, missing data causes code to output 0 for year missing
process_data = True

# Output from processing data
# Options are 'csv' or 'json'
output_type = 'csv'

# Regions of interest when processing data
# (0 = dark blue region, 1 = light blue, 2 = green, 3 = yellow , 4 = red)
regs_of_int = [0,1,2,3,4]



##############################
### STORM SPECIFIC OPTIONS ###
##############################

# Wind threshold, in knots
storm_thres = 34

# Duration threshold, in hours
storm_temporal_thres = 3

# time between one events start and a previous event in hours
storm_intervene = 96

# Wind speed spatial threshold, as a proportion of the grids
storm_spatial_t = .25



#############################
### WAVE SPECIFIC OPTIONS ###
#############################

# Wave threshold, in meters
wave_thres = 5

# Duration threshold, in hours
wave_temporal_thres = 3

# time between one event’s start and a previous event in hours
wave_intervene = 96

# Wind speed spatial threshold, as a proportion of the grids
wave_spatial_t = .25



#########################################################################################
### WARNING: Editing the variables below can break this code if improperly configured ###
#########################################################################################

# Path to geojson file. Leave as 'default' to use file included in this repo
# Use absolute paths only
geojson_file = 'default'

# Path to directory where .nc files are stored. Leave as 'default' to use the root level 'data' directory
# Use absolute paths only
data_dir = 'default'

# Path to directory where results files are stored. Leave as 'default' to use the root level 'results' directory
# Use absolute paths only
output_dir = 'default'

# These file base names are used to name and fetch the data files. Whatever is entered gets appended with '{year}.nc'
wave_data_base_name = 'Atlantic_waves_'
storm_data_base_name = 'Atlantic_stormy_'

# Variables lists that are sent to CDS API
wave_variable = ['mean_wave_period', 'significant_height_of_combined_wind_waves_and_swell']
storm_variable = ['10m_u_component_of_wind', '10m_v_component_of_wind', 'mean_sea_level_pressure','mean_wave_period', 'significant_height_of_combined_wind_waves_and_swell']