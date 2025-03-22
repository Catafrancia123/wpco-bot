import subprocess, sys, os
packages = ["discord.py", "rich", "playsound3", "pymongo"]

def clear():
    if sys.platform.startswith(('win32')):
        os.system('cls')
    elif sys.platform.startswith(('linux', 'cygwin', 'darwin', 'freebsd')):
        os.system('clear')

clear()
print("Setup\n")
while True:
    database_pkgs_confirm = str(input("Would you like to install pymongo (MongoDB)? (y/n)\n> "))
    if database_pkgs_confirm.lower() == "y":
        os.makedirs("pymongo-quickstart", exist_ok=True)

        if sys.platform.startswith("win32"):
            os.system("type nul > pymongo-quickstart\\quickstart.py")
        elif sys.platform.startswith(('linux', 'cygwin', 'darwin', 'freebsd')):
            os.system("touch pymongo-quickstart/quickstart.py")
        break
    elif database_pkgs_confirm.lower() == "n":
        packages.pop(packages.index("pymongo"))
        break
    else:
        print("Invalid Input.\n")

print(end=None)
subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--quiet"])
counter = 1
for i in packages:
    subprocess.run([sys.executable, "-m", "pip", "install", i,  "--quiet", "-U"])
    if counter >= 2:
        from rich import print as rprint
        rprint(f"[light_green][OK][/light_green] {i} has been installed. (PKG-{counter:02d})")
    else:
        print(f"[OK] {i} has been installed. (PKG-{counter:02d})")
    counter += 1
