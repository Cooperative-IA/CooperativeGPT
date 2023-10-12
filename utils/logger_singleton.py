import logging
import logging.config
import os
from datetime import datetime
import threading

CONFIG_DIR = "config"
LOG_DIR = "logs"


class LoggerSingleton:
    _instance = None
    _lock = threading.Lock()
    _current_agent = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerSingleton, cls).__new__(cls)
            cls._instance.setup_logging()
        return cls._instance


    def setup_logging(self):
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

    def acquire(self, agent_name):
        """Intenta adquirir el uso del singleton para un agente."""
        with self._lock:
            if self._current_agent is None:
                self._current_agent = agent_name
                return True
            return False

    def release(self, agent_name):
        """Libera el uso del singleton si el agente actual es el que lo está usando."""
        with self._lock:
            if self._current_agent == agent_name:
                self._current_agent = None

    def current_agent(self):
        """Devuelve el nombre del agente que está utilizando el singleton, o None si no hay ninguno."""
        return self._current_agent