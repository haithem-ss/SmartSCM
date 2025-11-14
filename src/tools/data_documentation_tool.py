import os
import yaml

from paths import DATA_PATH

def get_data_description():
    with open(os.path.join(DATA_PATH,"..","data_documentation.yaml" ),"r") as file:
        content = yaml.safe_load(file)
    return content
