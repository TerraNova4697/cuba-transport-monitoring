import json
import logging
import os
from dotenv import load_dotenv


logger = logging.getLogger()

load_dotenv()

CUBA_URL = os.environ["CUBA_URL"]
TB_GATEWAY_TOKEN = os.environ["TB_GATEWAY_TOKEN"]

# Load cameras.json
with open("./configs/transports.json", "r") as transports:
    transports = json.load(transports)

logger.info(f"Devices imported: {len(transports)}")
