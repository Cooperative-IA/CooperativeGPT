import logging
import logging.config
import os
from datetime import datetime

CONFIG_DIR = "config"
LOG_DIR = "logs"


def setup_logging():
    """Load logging configuration"""
    log_configs = {"dev": "logging.dev.ini", "prod": "logging.prod.ini", "debug": "logging.debug.ini"}
    config = log_configs.get(os.getenv("ENV"), "logging.dev.ini")
    config_path = os.path.join(CONFIG_DIR, config)

    timestamp = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")

    logging.config.fileConfig(
        config_path,
        disable_existing_loggers=False,
        defaults={"logfilename": timestamp},
    )