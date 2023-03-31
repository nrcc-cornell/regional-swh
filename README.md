# Regional SWH

Scripts to retrieve data from Climate Data Store Application Program Interface (CDS API) and process it into graphs for storms and waves.

## Requirements

- CDS API account
  - Go to https://cds.climate.copernicus.eu/api-how-to#use-the-cds-api-client-for-data-access and follow the instructions to set up an account and configure your system to access the API
  - NOTE: after registering and configuring, you will still need to agree to the Terms of Use of every dataset that you intend to download

- Anaconda
  - Ensure that you have Anaconda installed
  - Create environment from `environment.yml` by running `conda env create -n regional-swh --file environment.yml`

## Usage
1. Set up requirements
2. Edit `config.py` to suit your needs.
3. Ensure that the conda environment is active
4. Run `python main.py`
5. Results can be found in the `results` directory