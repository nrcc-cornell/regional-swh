import pathlib
import cdsapi

##########################
# Adjust these as needed #
##########################
start_year = 2000
end_year = 2001
##########################

data_dir = pathlib.Path(__file__).parent.parent.joinpath('data')

c = cdsapi.Client()
for yr in range(start_year, end_year):
  c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        'variable': [
            'mean_wave_period', 'significant_height_of_combined_wind_waves_and_swell',
        ],
        'year': [
            str(yr),
        ],
        'month': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
        ],
        'day': [
            '01', '02', '03',
            '04', '05', '06',
            '07', '08', '09',
            '10', '11', '12',
            '13', '14', '15',
            '16', '17', '18',
            '19', '20', '21',
            '22', '23', '24',
            '25', '26', '27',
            '28', '29', '30',
            '31',
        ],
        'time': [
            '00:00', '01:00', '02:00',
            '03:00', '04:00', '05:00',
            '06:00', '07:00', '08:00',
            '09:00', '10:00', '11:00',
            '12:00', '13:00', '14:00',
            '15:00', '16:00', '17:00',
            '18:00', '19:00', '20:00',
            '21:00', '22:00', '23:00',
        ],
        'area': [
            50, -80, 20,
            -60,
        ],
        'format': 'netcdf',
    },
    data_dir.joinpath(f'Atlantic_waves_{str(yr)}.nc')
  )