import json, os
from rich import print as rprint

def load_json(path : str, to_load : str, library : str = "none"): # loads stuff from json
    with open(path, mode="r", encoding="utf-8") as read_file:
        load = json.load(read_file)
    if library == "none":
        return load[to_load]
    return load[library][to_load]
pymongo_installed = True

try:
    from pymongo import MongoClient
    pymongo_installed = True
except ImportError:
    pymongo_installed = False

if pymongo_installed:
    MONGO_URL = load_json("config.json", "databaseToken")
    CLIENT = MongoClient(MONGO_URL)
SAVE = "save.json"

def find_save(method: str = "json"):
    save_found = False
    current_directory_files = os.listdir("./")
    if pymongo_installed and method.lower() == "mongodb":
        dblist = CLIENT.list_database_names()
        if "save" in dblist:
            save_found = True
            rprint(f'[[light_green]FOUND[/light_green]] Save file from MongoDB exists and continuing session.')
    elif not pymongo_installed and method.lower() == "mongodb":
        rprint(f"[[bright_red]ERROR[/bright_red]] pymongo not found, using alternative save.json file.")
        find_save("json")
    elif method.lower() == "json":
        if SAVE in current_directory_files:
            save_found = True

        if not save_found:
            rprint(f'[[bright_red]NOT FOUND[/bright_red]] Save file "save.json" doesn\'t exists and creating save file.')
            save_template = {
                "points" : {},
                "rank" : {},
                "user_data" : {}
            }

            with open("save.json", mode="w", encoding="utf-8") as outfile:
                json.dump(save_template, outfile)
            rprint(f'[[light_green]CREATED[/light_green]] Save file "save.json" has been created and continuing session.')
        else:
            rprint(f'[[light_green]FOUND[/light_green]] Save file "save.json" exists and continuing session.')

# TODO: add this
def load_mongodb(to_load : str):
    save_dir = CLIENT["save"]
    file = save_dir["save_file"]

    for i in file.find():
        print(i)

def edit_json(path : str, to_change : str, value, library : str = "none"): # Can edit/add
    with open(path, mode="r", encoding="utf-8") as read_file:
        data = json.load(read_file)
    if library != "none":
        data[library][to_change] = value
    else:
        data[to_change] = value

    with open(path, "w") as outfile:
        json.dump(data, outfile)

# Search algorithms (may come in handy later on)

def binary_search(array : list, target):
    low = 0
    high = len(array)

    while low <= high:
        mid = low + (high - low) // 2

        if array[mid] == target:
            return mid
        elif array[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    raise KeyError("Data not found.")