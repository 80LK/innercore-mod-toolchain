import json
import os
import os.path


class BaseConfig:
    def __init__(self, _json):
        self.json = _json

    def get_value(self, name, fallback=None):
        name = name.split(".")
        value = self.json
        while len(name) > 0 and len(name[0]) > 0:
            key = name.pop(0)
            if key in value:
                value = value[key]
            else:
                return fallback
        return value

    def get_config(self, name, not_none=False):
        value = self.get_value(name)
        if isinstance(value, dict):
            return BaseConfig(value)
        else:
            return BaseConfig({}) if not_none else None

    def get_filtered_list(self, name, prop, values):
        value = self.get_value(name)
        if isinstance(value, list):
            filtered = []
            for obj in value:
                if isinstance(obj, dict) and prop in obj and obj[prop] in values:
                    filtered.append(obj)
            return filtered
        else:
            return []


class MakeConfig(BaseConfig):
    def __init__(self, filename):
        self.filename = filename
        self.root_dir = os.path.abspath(os.path.join(self.filename, ".."))
        with open(filename, encoding="utf-8") as file:
            self.json = json.load(file)
        BaseConfig.__init__(self, self.json)

    def get_root_dir(self):
        return self.root_dir

    def get_path(self, relative_path):
        return os.path.abspath(os.path.join(self.root_dir, relative_path))

    def get_paths(self, relative_path, filter=None, paths=None):
        if paths is None:
            paths = []
        if len(relative_path) > 0 and relative_path[-1] == "*":
            path = self.get_path(relative_path[:-1])
            if not os.path.isdir(path):
                return []
            for f in os.listdir(path):
                file = os.path.join(path, f)
                if filter is None or filter(file):
                    paths.append(file)
        else:
            path = self.get_path(relative_path)
            if filter is None or filter(path):
                paths.append(path)
        return paths


# search for make.json
make_config = None
for i in range(0, 4):
    make_file = os.path.join("../" * i, "make.json")
    if os.path.isfile(make_file):
        make_config = MakeConfig(make_file)
        break
if make_config is None:
    raise RuntimeError("failed to find make.json")


if __name__ == '__main__':
    print(make_config.get_value("native"))

