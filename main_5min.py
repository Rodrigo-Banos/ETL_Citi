import pandas as pd   
import os  
import sys  
import time  

start_time_code = time.time()

# Create folder strings and read directories
DIR_BASE = os.getcwd()  # Current working directory
OUTPUT_URL = 'output'  # For output files
SOURCE_URL = 'source'  # For sources
INPUT_URL = 'input'  # Input files

# Create folders in the cwd
sys.path.append(os.path.join(OUTPUT_URL))
sys.path.append(os.path.join(SOURCE_URL))
sys.path.append(os.path.join(INPUT_URL))

import 5min_Network_Traffic_ETL  

# Execute the main function from the imported module
result = 5min_Network_Traffic_ETL.main(DIR_BASE, INPUT_URL, OUTPUT_URL)

end_time = time.time()
elapsed_time = round(end_time - start_time_code, 1)

hours, rem = divmod(elapsed_time, 3600)
minutes, seconds = divmod(rem, 60)

# Print the elapsed time
print(
    "\n" + "-" * 10 + " PROCESS FINISHED " + "-" * 10 + "\n"
    f"Elapsed time:\n"
    f"H: {int(hours)}\n"
    f"M: {int(minutes)}\n"
    f"S: {int(seconds)}\n"
)