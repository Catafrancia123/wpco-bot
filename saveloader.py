import json, os, datetime
from rich import print as rprint

try:
    from pymongo import MongoClient
    pymongo_installed = True
except ImportError:
    pymongo_installed = False

#* sorry for one liner but, i cant put a function above constant variables :)
CHOOSE_SAVE = (load := json.load(open("config.json", "r", encoding="utf-8")))["settings"]["run_bot_on"]
if pymongo_installed:
    MONGO_URL = (load := json.load(open("config.json", "r", encoding="utf-8")))["databaseToken"]
    db = MongoClient(MONGO_URL)
SAVES = ("save_wpco.json")
save_template = {
    "points" : {},
    "user_data" : {}
}

def find_save(method: str = "json"):
    save_found = False
    current_directory_files = os.listdir("./")
    if pymongo_installed and method.lower() == "mongodb":
        if not pymongo_installed:
            rprint(f"[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[bright_red]ERROR[/bright_red]] pymongo not found, using alternative {SAVES[SAVES.index(CHOOSE_SAVE)]} file.")
            find_save("json")
        dblist = db.list_database_names()
        if f"save-{CHOOSE_SAVE}" in dblist:
            save_found = True
            rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[light_green]FOUND[/light_green]] Save file from MongoDB exists and continuing session.')

        if not save_found:
            save_dir = db[f"save-{CHOOSE_SAVE}"]
            save_file = save_dir["save-file"]
            save_file.insert_one(save_template)
    elif method.lower() == "json":
        for i in SAVES:
            if i not in current_directory_files:
                save_found = False
            elif i in current_directory_files:
                save_found = True

        if not save_found:
            rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[bright_red]NOT FOUND[/bright_red]] Save files doesn\'t exists and creating save file.')
            with open(f"save_{CHOOSE_SAVE}.json", mode="w", encoding="utf-8") as outfile:
                json.dump(save_template, outfile)
                outfile.close()
            rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[light_green]CREATED[/light_green]] Save files have been created and continuing session.')
        else:
            rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[light_green]FOUND[/light_green]] Save files exists and continuing session.')

def load_json(path : str, to_load : str, library : str = None) -> any: #* loads stuff from json
    with open(path, mode="r", encoding="utf-8") as read_file:
        load = json.load(read_file)
        
    #* json throws a keyerror if the data is not found.
    if library != None:
        data = load[library][to_load]
    elif library == None:
        data = load[to_load]

    read_file.close()
    return data

def load_mongodb(to_load: str, object: str = None, index: int = 1) -> any: #* online db integration (yippee!!!)
    if not pymongo_installed:
        raise ImportError("pymongo not found, you haven't installed it you goober.")
    else:
        file = db[f"save-{CHOOSE_SAVE}"]["save-file"]
        if object != None:
            filt = {"_id": index, f"{object}.{to_load}": {"$exists": True}}
            result = file.find_one(filt)
            
            if result == None:
                raise KeyError("Object/Key not found.")
            else:
                return result[object][to_load]
        elif object == None:
            filt = {"_id": index, to_load: {"$exists": True}}
            result = file.find_one(filt)

            if result == None:
                raise KeyError("Key not found.")
            else:
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

def edit_mongodb(to_edit: str, value, object: str = None, index: int = 1):
    if not pymongo_installed:
        raise ImportError("pymongo not found, you haven't installed it you goober.")
    else:
        file = db[f"save-{CHOOSE_SAVE}"]["save-file"]
        if object != None:
            filt = {"_id": index, object: {"$exists": True}}
            update = {"$set": {f"{object}.{to_edit}": value}}
            #* check if the field exists
            check_exist = file.find_one(filt)
            if check_exist == None:
                #* create new field
                file.update_one({"_id": index}, {"$set": {object: {}}})
        elif object == None:
            filt = {}
            update = {"$set": {to_edit: value}}
        file.update_one(filt, update)

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