"""
Basic wrapper around datadog api
"""
import logging
import os
from pathlib import Path
from typing import Optional

import yaml
from datadog import initialize, api

MAX_RETRY = 10


class DatadogClient:

    home = str(Path.home())
    config_dir = ".doghouse"
    config_file = "config.yml"
    default_config_file = f"{home}/{config_dir}/{config_file}"

    def __init__(self):
        config = self.__load_config()
        if not config:
            config = self._create_config_file()
        initialize(api_key=config["api_key"], app_key=config["app_key"])

    def __load_config(self) -> Optional[dict]:
        config_file = self.default_config_file
        if not os.path.exists(config_file):
            return None
        with open(config_file, "r") as config_dict:
            try:
                return yaml.safe_load(config_dict)
            except yaml.YAMLError as ex:
                logging.error(
                    "Couldn't find config.yaml file; is it in the ~/.doghouse directory? "
                )
                raise ex

    def _create_config_file(self, api_key=None, app_key=None) -> dict:
        """ Create the config file from user input if it doesn't already exist."""
        if not api_key:
            api_key = input("Please enter your API Key: ")
        if not app_key:
            app_key = input("Please enter your APP Key: ")
        config = {"api_key": api_key, "app_key": app_key}
        with open(self.default_config_file, "w+") as new_config:
            yaml.dump(config, new_config, default_flow_style=False)
        print(f"💾 Created config file at {self.default_config_file}")
        return config

    def get_dashboards(self):
        return api.Dashboard.get_all()["dashboards"]

    def get_dashboard_detail(self, dashboard_id):
        return api.Dashboard.get(dashboard_id)

    def update_dashboard(self, dashboard_id, **kwargs):
        return api.Dashboard.update(dashboard_id, **kwargs)

    def get_monitors(self):
        return api.Monitor.get_all()

    def update_monitor(self, monitor_id, **kwargs):
        return api.Monitor.update(monitor_id, **kwargs)

    def configure(self, api_key, app_key):
        self._create_config_file(api_key, app_key)
