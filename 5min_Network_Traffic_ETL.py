import warnings
warnings.filterwarnings("ignore")

# import threading
# import concurrent.futures
# import pyodbc
import pandas as pd
import os
import requests
from io import StringIO
# import shutil
# import re
import time
import logging
from datetime import datetime, timedelta
from pytz import timezone

# Credentials & Variables
today_date = f'{pd.Timestamp.today().strftime("%Y%m%d")}'
yesterday_date_uploading = f'{(pd.Timestamp.today() - pd.Timedelta(days=1)).strftime("%Y%m%d")}'
today_time = f'{pd.Timestamp.today().strftime("%H_%M_%S")}'

# NetOps API access credentials (move to a config file for security)
credentials = {
    "username": "user",
    "password": "password"
}

target_group = "Network_DB_Collection"

# API Variables
today = datetime.now(timezone("UTC"))  # Get current UTC time
collection_days = 2

# Date calculations
start_date = today - timedelta(days=collection_days)
start_date_00 = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
start_date_00_timestamp = round(start_date_00.timestamp())

end_date = today - timedelta(days=0)
end_date_00 = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
end_date_00_timestamp = round(end_date_00.timestamp())

# API URL
validation_API_url = "https://cawspmag02a.latam.nsroot.net:8582/odata/api/interfaces?"

# Functions
def create_log_file(DIR_BASE, OUTPUT_URL, today_export_folder):
    log_filename = f"{DIR_BASE}/{OUTPUT_URL}/{today_export_folder}/LOG_5_min_col_{today_date}_{today_time}.log"
    logging.basicConfig(filename=log_filename, level=logging.DEBUG)
    logging.info(f"Execution Date: {today_date} | Execution Time: {today_time}")

def api_validation():
    try:
        validation_API = requests.get(validation_API_url, auth=(credentials["username"], credentials["password"]), verify=False)
        response_validation_API = pd.read_csv(StringIO(validation_API.text))
        print("\nValidation API connection successful:\n\n", response_validation_API.head(1))
        logging.info(f"{today_time}: Validation API connection successful \n")
    except TypeError as err:
        logging.exception(f"{today_time}: API connection FAILED \n")
        raise TypeError(f"Parsing issue with the API: {validation_API_url}\n{str(err)}")

def data_collection_5min(DIR_BASE, OUTPUT_URL, today_export_folder, stop, top, skip, icount):
    while top <= stop:
        try:
            collection_API_url = (
                f"https://caswpmagg01p.nam.nsroot.net:8582/odata/api/interfaces?"
                f"&resolution=RATE&starttime={start_date_00_timestamp}&endtime={end_date_00_timestamp}&tz=UTC"
                f"&$top={top}&$skip={skip}&$expand=device,portmfs"
                f"&$select=device/ID,device/Name,ID,Description,SpeedIn,SpeedOut,IPAddresses,"
                f"portmfs/Resolution,portmfs/Timestamp,portmfs/im_UtilizationIn,portmfs/im_UtilizationOut"
                f"&$filter=(groups/Name eq '{target_group}')"
            )

            collection_API = requests.get(collection_API_url, auth=(credentials["username"], credentials["password"]), verify=False)
            response_Collection_API = pd.read_csv(StringIO(collection_API.text))

            print(f"\n\nCollection API (Skip: {skip}):\n\n")
            print(f"Stop: {stop} | Top: {top} | Skip: {skip} | icount: {icount}")

            top += icount
            skip += icount

        except TypeError as err:
            logging.exception(f"{today_time}: API connection FAILED \n")
            raise TypeError(f"Parsing Issue with the API: {collection_API_url}\n{str(err)}")

        return response_Collection_API

def sequential_data_collection(DIR_BASE, OUTPUT_URL, today_export_folder):
    fixed_args = (DIR_BASE, OUTPUT_URL, today_export_folder)
    variable_args_list = [
        (1000, 100, 0, 100),
        (1000, 100, 1000, 100),
        (1000, 100, 2000, 100)
    ]

    final_resampled_dataframe = pd.DataFrame()

    def execute_single_iteration(var_args, iteration):
        try:
            result = data_collection_5min(*fixed_args, *var_args)
            if isinstance(result, pd.DataFrame):
                result["Iteration"] = iteration
                return result
        except Exception as exc:
            print(f"Generated an exception: {exc}")
        return None

    for iteration, var_args in enumerate(variable_args_list, start=1):
        result = execute_single_iteration(var_args, iteration)
        if result is not None:
            final_resampled_dataframe = pd.concat([final_resampled_dataframe, result], ignore_index=True)
        time.sleep(15)  # Wait for 15 seconds between iterations

    final_resampled_dataframe.to_csv(
        f"{DIR_BASE}/{OUTPUT_URL}/{today_export_folder}/1_raw_response_Collection_API_{today_export_folder}.csv",
        index=False
    )

    return final_resampled_dataframe

def main(DIR_BASE, INPUT_URL, OUTPUT_URL):
    files = os.listdir(INPUT_URL)
    today_export_folder = f"{today_date}_{today_time}"
    os.mkdir(f"{DIR_BASE}/{OUTPUT_URL}/{today_export_folder}")

    create_log_file(DIR_BASE, OUTPUT_URL, today_export_folder)
    api_test = api_validation()

    raw_data_collection = sequential_data_collection(DIR_BASE, OUTPUT_URL, today_export_folder)

    print("\nModules Successfully Loaded\n")
    print(pd.__version__)