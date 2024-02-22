from collections.abc import Mapping
import logging
import logging.config
import os
from datetime import datetime
from typing import Any

CONFIG_DIR = "config"
LOG_DIR = "logs"


def setup_logging(timestamp):
    """Load logging configuration"""
    # Create the log directory if it doesn't exist
    if not os.path.exists(os.path.join(LOG_DIR,str(timestamp))):
        os.makedirs(os.path.join( LOG_DIR,str(timestamp)))
        
    log_configs = {"dev": "logging.dev.ini", "prod": "logging.prod.ini", "debug": "logging.debug.ini"}
    config = log_configs.get(os.getenv("ENV"), "logging.dev.ini")
    config_path = os.path.join(CONFIG_DIR, config)

    

    logging.config.fileConfig(
        config_path,
        disable_existing_loggers=False,
        defaults={"logfilename":f'{str(timestamp)}/{str(timestamp)}', "customArg": "Hello"},
    )

class CustomAdapter(logging.LoggerAdapter):
    """
    Adapter to pass extra context to the logger
    """
    def __new__(cls, logger: logging.Logger, extra: dict[str, Any] = {}, game_env = None) -> logging.LoggerAdapter:
        """
        Constructor for the CustomAdapter class

        Args:
            logger (logging.Logger): Logger
            extra (Mapping[str, Any]): Extra information to pass to the logger
            game_env (GameEnvironment): Game environment

        Returns:
            logging.LoggerAdapter: Logger adapter
        """
        # Reuse the game_env from the previous adapter
        if not game_env:
            game_env = getattr(cls, 'prev_game_env', None)
        
        if not hasattr(cls, 'prev_game_env') and game_env:
            cls.prev_game_env = game_env

        instance = super().__new__(cls)
        return instance
    
    def __init__(self, logger: logging.Logger, extra: dict[str, Any] = {}, game_env = None) -> None:
        """
        Logger adapter to pass game environment information to the logger

        Args:
            logger (logging.Logger): Logger
            extra (Mapping[str, Any]): Extra information to pass to the logger
            game_env (GameEnvironment): Game environment
        """
        super().__init__(logger, extra)
        if not game_env:
            game_env = getattr(self, 'prev_game_env', None)

        self.game_env = game_env

    def process(self, msg: str, kwargs: Mapping[str, Any]) -> tuple[str, Mapping[str, Any]]:
        """
        Adds the game time to the log message
        """
        game_time = None
        step = None

        # If the game environment exists, get the game time and the step
        if self.game_env:
            game_time = self.game_env.get_time()
            step = self.game_env.get_current_step_number()
        # If the game environment doesn't exist, get it from the previous adapter
        else:
            self.game_env = getattr(self, 'prev_game_env', None)
            if self.game_env:
                game_time = self.game_env.get_time()
                step = self.game_env.get_current_step_number()

        # Add yhe game time and step to the log message
        kwargs["extra"] = {"game_time": game_time, "step": step}
        return msg, kwargs

class CustomFormatter(logging.Formatter):
    def format(self, record):
        
        # If the game time doesn't exist, set it to "None"
        if getattr(record, "game_time", None) is None:
            record.game_time = "None"

        # If the game step doesn't exist, set it to "None"
        if getattr(record, "step", None) is None:
            record.step = 0
        
        return super().format(record)