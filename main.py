from fetch_data import fetch_data
from process_data import process_data

import config

if config.data_type == 'both':
    data_types = ['storm', 'wave']
else:
    data_types = [config.data_type]

for data_type in data_types:
    print(f'Fetching {data_type} data...')
    if config.fetch_data:
        fetch_data(data_type)

    print(f'Processing {data_type} data...')
    if config.process_data:
        process_data(data_type)