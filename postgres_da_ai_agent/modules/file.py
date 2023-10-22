import json
import yaml


def write_file(file_name, content):
    with open(file_name, "w") as file:
        file.write(content)


def write_json_file(file_name, content):
    with open(file_name, "w") as file:
        json.dump(content, file)


def write_yml_file(file_name, content):
    with open(file_name, "w") as file:
        yaml.dump(content, file)
