# utils/logger.py

import logging
import os
from datetime import datetime
from utils.s3_utils import upload_file

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def get_logger(session_id: str):

    logger = logging.getLogger(session_id)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    log_file = os.path.join(LOG_DIR, f"{session_id}.log")

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# -------------------------------
# Upload log to S3
# -------------------------------
def upload_log_to_s3(session_id: str):

    log_path = f"{LOG_DIR}/{session_id}.log"

    try:
        upload_file(log_path, f"logs/{session_id}.log")
    except Exception as e:
        print(f"Failed to upload log: {e}")