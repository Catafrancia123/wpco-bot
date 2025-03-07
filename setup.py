import subprocess, sys, os
packages = ["discord.py", "rich", "playsound3", "pymongo"]
print("Ignore the warning above\n")

def clear():
    if sys.platform.startswith(('win32')):
        os.system('cls')
    elif sys.platform.startswith(('linux', 'cygwin', 'darwin', 'freebsd')):
        os.system('clear')

clear()
while True:
    database_pkgs_confirm = str(input("Would you like to install pymongo (MongoDB)? (y/n)\n> "))
    if database_pkgs_confirm.lower() == "y":
        os.system("mkdir pymongo-wpco-bot")
        os.system("cd pymongo-wpco-bot")

        if sys.platform.startswith("win32"):
            os.system("type nul > quickstart.py")
            os.system("py -m venv venv")
            os.system(". venv\Scripts\activate")
        elif sys.platform.startswith(('linux', 'cygwin', 'darwin', 'freebsd')):
            os.system("touch quickstart.py")
            os.system("python3 -m venv venv")
            os.system("source venv/bin/activate")
        break
    elif database_pkgs_confirm.lower() == "n":
        packages.pop(packages.index("pymongo"))
        break
    else:
        print("Invalid Input.\n")

counter = 1
for i in packages:
    subprocess.run([sys.executable, "-m", "pip", "install", i,  "--quiet", "-U"])
    print(f"[OK] {i} has been installed. (PKG-{counter:02d})")
    counter += 1
