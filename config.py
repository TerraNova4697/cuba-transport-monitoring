"""
Configurations and global variables.
"""

import logging
import os
from dotenv import load_dotenv


logger = logging.getLogger()

load_dotenv()

# Load environment variables.
CUBA_URL = os.environ["CUBA_URL"]
TB_GATEWAY_TOKEN = os.environ["TB_GATEWAY_TOKEN"]
