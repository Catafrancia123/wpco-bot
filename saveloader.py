import json, os, datetime
from rich import print as rprint

try:
    from pymongo import MongoClient
    pymongo_installed = True
except ImportError:
    pymongo_installed = False

if pymongo_installed:
    #* sorry for one liner but, i cant put a function above constant variables :)
    MONGO_URL = (load := json.load(open("config.json", "r", encoding="utf-8")))["databaseToken"]
    CLIENT = MongoClient(MONGO_URL)
CHOOSE_SAVE = (load := json.load(open("config.json", "r", encoding="utf-8")))["settings"]["run_bot_on"]
SAVES = ("save_wpco.json", "save_goc.json")

def find_save(method: str = "json"):
    save_found = False
    current_directory_files = os.listdir("./")
    if pymongo_installed and method.lower() == "mongodb":
        dblist = CLIENT.list_database_names()
        if "save" in dblist:
            save_found = True
            rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[light_green]FOUND[/light_green]] Save file from MongoDB exists and continuing session.')
    elif not pymongo_installed and method.lower() == "mongodb":
        rprint(f"[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[bright_red]ERROR[/bright_red]] pymongo not found, using alternative {SAVES[SAVES.index(CHOOSE_SAVE)]} file.")
        find_save("json")
    elif method.lower() == "json":
        for i in SAVES:
            if i not in current_directory_files:
                save_found = False
            elif i in current_directory_files:
                save_found = True

        if not save_found:
            rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[bright_red]NOT FOUND[/bright_red]] Save files doesn\'t exists and creating save file.')
            save_template_wpco = {
                "points" : {},
                "rank" : {},
                "user_data" : {}
            }

            save_template_goc = {
                "points" : {},
                "user_data" : {}
            }

            with open(SAVES[SAVES.index(CHOOSE_SAVE)], mode="w", encoding="utf-8") as outfile:
                if CHOOSE_SAVE == "wpco":
                    json.dump(save_template_wpco, outfile)
                elif CHOOSE_SAVE == "goc":
                    json.dump(save_template_goc, outfile)
                outfile.close()
            rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[light_green]CREATED[/light_green]] Save file "{SAVES[0]}" and "{SAVES[1]}" has been created and continuing session.')
        else:
            rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[light_green]FOUND[/light_green]] Save file "{SAVES[0]}" and "{SAVES[1]}" exists and continuing session.')

def load_json(path : str, to_load : str, library : str = None): #* loads stuff from json
    with open(path, mode="r", encoding="utf-8") as read_file:
        load = json.load(read_file)
        
    if library != None:
        data = load[library][to_load]
    elif library == None:
        data = load[to_load]

    read_file.close()
    return data

def load_mongodb(to_load : str, library: str = None): #* online db integration (yippe!!!)
    if pymongo_installed == False:
        raise ImportError("pymongo not found, you haven't installed it you goober.")
    else:
        save_dir = CLIENT["save"]
        file = save_dir["save_file"]
        
        result = file.find_one({}, {f"{library}.{to_load}": 1})
        if library != None:
            if result and library in result and to_load in result[library]:
                return result[library][to_load]
            else:
                raise KeyError(f"{to_load} not found in {library}")
        elif library == None:
            return result[to_load]

def edit_json(path : str, to_change : str, value, library : str = None): #* Can edit/add
    with open(path, mode="r", encoding="utf-8") as read_file:
        data = json.load(read_file)
        
    if library != None:
        data[library][to_change] = value
    elif library == None:
        data[to_change] = value
    read_file.close()

    with open(path, "w") as outfile:
        json.dump(data, outfile)
    outfile.close()

#! Search algorithms (may come in handy later on). DONT DELETE THIS.

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