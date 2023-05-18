from os import listdir
from os.path import isfile, join
import yaml as yaml_


class ConfigReader:
    def __init__(self, configs_dir: str):
        self.configs_dir = configs_dir
        self.yaml_files = self.__get_yaml_files()
        self.config_names = self.__get_config_names()
        self.configs_with_names = self.__get_configs()

    def __get_config_names(self) -> list:
        config_names = [f.replace(".yaml", "") for f in self.yaml_files]
        return config_names

    def __get_yaml_files(self) -> list:
        yaml_files = [
            f for f in listdir(self.configs_dir)
            if isfile(join(self.configs_dir, f)) and f.endswith("yaml")]

        return yaml_files

    def __get_configs(self) -> dict:
        configs = [
            yaml_.load(open(join(self.configs_dir, yaml)), Loader=yaml_.SafeLoader)
            for yaml in self.yaml_files
        ]
        configs_with_names = {k: v for k, v in zip(self.config_names, configs)}
        return configs_with_names
