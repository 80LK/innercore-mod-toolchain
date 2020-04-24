import os
import os.path
import sys
import json
from os import getcwd

from base_config import BaseConfig

from utils import clear_directory, copy_directory, ensure_directory, copy_file
import zipfile



def setup_mod_info(make_file):
    name = input("Enter project name: ")
    author = input("Enter author name: ")
    version = input("Enter project version [1.0]: ")
    description = input("Enter project description: ")

    make_file["global"]["info"] = {
        "name": name,
        "author": author,
        "version": version,
        "description": description
    }



def init_java_and_native(make_file, directory):
    compile_dirs = []

    src_dir = os.path.join(directory, "src")

    sample_native_module = os.path.join(src_dir, "native", "sample")
    if not os.path.exists(sample_native_module):
        print("native sample module is unavailable")

    else:
        res = input("Do you want to initialize a new native directory? [y/N]: ")
        if res.lower() == 'y':
            module_name = input("Enter the new native module name [sample]: ")
            if module_name != "":
                os.rename(sample_native_module,
                    os.path.join(src_dir, "native", module_name))
        else:
            if(os.path.isdir(sample_native_module)):
                clear_directory(sample_native_module)


    sample_java_archive = os.path.join(src_dir, "java.zip")
    if(not os.path.exists(sample_java_archive)):
        print("java sample module is unavailable")
    else: 
        res = input("Do you want to initialize a new java directory? [y/N]: ")
        if res.lower() == 'y':
            module_name = input("Enter the new java module name [sample]: ")
            if module_name == "":
                module_name = "sample"

            with zipfile.ZipFile(sample_java_archive, 'r') as zip_ref:
                zip_ref.extractall(os.path.join(src_dir))

            os.rename(os.path.join(src_dir, "java", "sample"),
                os.path.join(src_dir, "java", module_name))

            # write info to .classpath
            import xml.etree.ElementTree as etree
            classpath = os.path.join(directory, ".classpath")
            tree = etree.parse(classpath)
            for classpathentry in tree.getroot():
                if(classpathentry.attrib["kind"] == "src"):
                    classpathentry.attrib["path"] = "src/java/" + module_name + "/src"

            tree.write(classpath, encoding="utf-8", xml_declaration=True)
            
        else:
            if(os.path.isfile(sample_java_archive)):
                os.remove(sample_java_archive)


def cleanup_if_required(directory):
    res = input("Do you want to clean up the project? [Y/n]: ")
    if res.lower() == 'n':
        return

    to_remove = [
        "toolchain-setup.py",
        "toolchain-import.py",
        "toolchain.zip"
    ]
    for f in to_remove:
        path = os.path.join(directory, f)
        if(os.path.exists(path)):
            os.remove(path)


def init_directories(directory):
    assets_dir = os.path.join(directory, "src", "assets")
    clear_directory(assets_dir)
    os.makedirs(os.path.join(assets_dir, "gui"))
    os.makedirs(os.path.join(assets_dir, "res", "items-opaque"))
    os.makedirs(os.path.join(assets_dir, "res", "terran-atlas"))
    libs_dir = os.path.join("src", "lib")
    clear_directory(libs_dir)
    os.makedirs(libs_dir)
    with(open(os.path.join(directory, "src", "dev", "header.js"), "w", encoding="utf-8")) as file:
        file.write("")
        



print("running project setup script")

destination = sys.argv[1]
make_path = os.path.join(destination, "make.json")

if not (os.path.exists(make_path)):
    exit("invalid arguments passed to import script, usage: \r\npython setup.py <destination>")

with open(make_path, "r", encoding="utf-8") as make_file:
    make_obj = json.loads(make_file.read())

if destination == '.':
    dirname = os.path.dirname(os.getcwd())
else: 
    dirname = os.path.dirname(destination)

make_obj["make"]["pushTo"] = "storage/emulated/0/games/horizon/packs/innercore-dev/innercore/mods/" + dirname
print("initializing mod.info")
setup_mod_info(make_obj)
print("initializing required directories")
init_directories(destination)
print("initializing java and native modules")
init_java_and_native(make_obj, destination)
cleanup_if_required(destination)


with open(make_path, "w", encoding="utf-8") as make_file:
    make_file.write(json.dumps(make_obj, indent=" " * 4))

print("project successfully imported, please, delete project.back after triple checking that everything is OK")