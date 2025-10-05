import os
from dotenv import load_dotenv
import logger_config
import logging

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
logger.info(f"GEMINI_MODEL set to: {GEMINI_MODEL}")