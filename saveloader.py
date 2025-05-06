import json, os, datetime
from rich import print as rprint

try:
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
    from motor import MotorCollection
    pymongo_installed = True
except ImportError:
    pymongo_installed = False

#* sorry for one liner but, i cant put a function above constant variables :)
CHOOSE_SAVE = (load := json.load(open("config.json", "r", encoding="utf-8")))["settings"]["run_bot_on"]
if pymongo_installed:
    MONGO_URL = (load := json.load(open("config.json", "r", encoding="utf-8")))["databaseToken"]
    db = AsyncIOMotorClient(MONGO_URL)
SAVES = ("save_wpco.json")
save_template = {
    "points" : {},
    "user_data" : {}
}

async def find_save(method: str = "json"):
    """Finds the save file in 2 different methods: MongoDB or JSON.

    Parameters
    ----------
    method: str = "json"
        The argument to choose the method (default = json)
    """
    
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

def load_json(path : str, to_load : str, object : str = None) -> any: #* loads stuff from json
    """Loads data from a JSON file.
    
    Parameters
    ----------
    path: str
        The path of the JSON file to access.
    to_load: str
        The data to load.
    object: str = None
        The object inside the JSON file to access to find to_load

    Raises
    ------
    FileNotFoundError
        If the file wasn't found/doesn't exist.
    KeyError
        If the JSON library didn't find the object/key
    """

    if not os.path.exists(path):
        raise FileNotFoundError("ERR 404: File not found.")
    else:
        with open(path, mode="r", encoding="utf-8") as read_file:
            load = json.load(read_file)
            
        #* json throws a keyerror if the data is not found.
        if object != None:
            data = load[object][to_load]
        elif object == None:
            data = load[to_load]

        read_file.close()
        return data

async def load_mongodb(file: AsyncIOMotorCollection, to_load: str, object: str = None, index: int = 1) -> any: #* online db integration (yippee!!!)
    """Loads data in a MongoDB collection.
    
    Parameters
    ----------
    file: AsyncIOMotorCollection
        The collection to access.
    to_load: str
        The name of the data to load.
    object: str = None
        The object inside the collection to access to find to_load
    index: int = 1
        The document index to access (defaults to 1)
        
    Raises
    ------
    ImportError
        If you didn't install pymongo and ran this command.
    KeyError
        If the object/key wasn't found."""
    
    if not pymongo_installed:
        raise ImportError("pymongo not found, you haven't installed it you goober.")
    else:
        if object != None:
            filt = {"_id": index, f"{object}.{to_load}": {"$exists": True}}
            result = await file.find_one(filt)
            
            if result == None:
                raise KeyError("Object/Key wasn't found.")
            else:
                return result[object][to_load]
        elif object == None:
            filt = {"_id": index, to_load: {"$exists": True}}
            result = await file.find_one(filt)

            if result == None:
                raise KeyError("Key wasn't found.")
            else:
                return result[to_load]
            
def edit_json(path : str, to_change : str, value: any, object : str = None): #* Can edit/add
    """Edits data in a JSON file.
    
    Parameters
    ----------
    path: str
        The path of the JSON file to access.
    to_change: str:
        The name of the data to change.
    value: any
        The value to change the specified data
    object: str = None
        The object inside the JSON file to access to find to_change
        
    Raises
    ------
    FileNotFoundError
        If the file wasn't found/doesn't exist.
    KeyError
        If the JSON library didn't find the object/key"""
    if not os.path.exists(path):
        raise FileNotFoundError("ERR 404: File not found.")
    else:
        with open(path, mode="r", encoding="utf-8") as read_file:
            data = json.load(read_file)
            
        if object != None:
            data[object][to_change] = value
        elif object == None:
            data[to_change] = value
        read_file.close()

        with open(path, "w") as outfile:
            json.dump(data, outfile)
        outfile.close()

async def edit_mongodb(file: AsyncIOMotorCollection, to_edit: str, value: any, object: str = None, index: int = 1):
    """Edits data in a MongoDB collection.
    
    Parameters
    ----------
    file: AsyncIOMotorCollection
        The collection to access.
    to_edit: str
        The name of the data to change
    value: any
        The value to change the data
    object: str = None
        The object inside the collection to access to find to_load
    index: int = 1
        The document index to access (defaults to 1)
        
    Raises
    ------
    ImportError
        If you didn't install pymongo and ran this command.
    KeyError
        If the object/key wasn't found."""
    
    if not pymongo_installed:
        raise ImportError("pymongo not found, you haven't installed it you goober.")
    else:
        if object != None:
            filt = {"_id": index, object: {"$exists": True}}
            update = {"$set": {f"{object}.{to_edit}": value}}
            #* check if the field exists
            check_exist = await file.find_one(filt)
            if check_exist == None:
                #* create new field
                await file.update_one({"_id": index}, {"$set": {object: {}}})
        elif object == None:
            filt = {}
            update = {"$set": {to_edit: value}}
        await file.update_one(filt, update)

#! Search algorithms (may come in handy later on). DONT DELETE THIS.

def binary_search(array : list, target) -> any:
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
