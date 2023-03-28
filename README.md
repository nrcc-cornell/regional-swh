# Regional SWH

Scripts to retrieve data from Climate Data Store Application Program Interface (CDS API) and process it into graphs for storms and waves.

## Requirements

- CDS API account
  - Go to https://cds.climate.copernicus.eu/api-how-to#use-the-cds-api-client-for-data-access and follow the instructions to set up an account and configure your system to access the API
  - NOTE: after registering and configuring, you will still need to agree to the Terms of Use of every dataset that you intend to download

- Anaconda
  - There is a conda environment spec file in the conda_env directory. Please use it to create the necessary environment to run these scripts.

## Usage
1. Set up requirements
2. Ensure that the conda environment is active

Where XXXX = [storm|wave]:
3. In `XXXX_scripts/fetch_XXXXs_data.py` and `XXXX_scripts/process_XXXXs_data.py` set the start_year and end_year variables to your desired years
4. Run `python XXXX_scripts/fetch_XXXXs_data.py` to fetch data
   - Data can be found in the `data` directory
5. Run `python XXXX_scripts/process_XXXXs_data.py` to process data
   - Results can be found in `results` directory