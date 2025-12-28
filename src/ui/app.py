from src.api import decode_vin_values_extended, print_vin_values_extended
from src.logs import logs

import logging

if __name__ == "__main__":
    logger = logs.setup_logger(logging.DEBUG, logging.ERROR)
    logger.info("Logger Initialized")
    print("Welcome to pyVIN!")
    vin_to_decode = "19UUA56922A021559"
    try:
        response = decode_vin_values_extended(vin_to_decode)
        print_vin_values_extended(response)
    except Exception as e:
        print(f"Error: {e}")