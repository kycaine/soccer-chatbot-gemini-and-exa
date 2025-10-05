import logging
import os
from dotenv import load_dotenv

load_dotenv()

DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

if DEBUG_MODE:
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=logging.INFO, 
        format=log_format,
        handlers=[logging.StreamHandler()]
    )
    
    logging.getLogger(__name__).info("Debug mode is ON. Logging is enabled.")
else:
    logging.disable(logging.CRITICAL)