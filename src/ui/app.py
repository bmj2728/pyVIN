from src.logs import logs
import logging

if __name__ == "__main__":
    logger = logs.setup_logger(logging.DEBUG, logging.ERROR)
    logger.info("Logger Initialized")
    print("Welcome to pyVIN!")