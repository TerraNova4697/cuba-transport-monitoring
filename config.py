import json
import logging


logger = logging.getLogger()

# Load config.json
with open("./configs/config.json", "r") as config:
    CONFIGS = json.load(config)

CUBA_URL = CONFIGS["CUBA_URL"]

# Load cameras.json
with open("./configs/transports.json", "r") as transports:
    transports = json.load(transports)

logger.info(f"Devices imported: {len(transports)}")
