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
subprocess.run([sys.executable, "-m", "pip", "install", "-U", "pip", "-q"], check=True)
counter = 1
for package in packages:
    subprocess.run([sys.executable, "-m", "pip", "install", package,  "-q", "-U"], check=True)
    if counter >= 2:
        from rich import print as rprint
        rprint(f"[light_green][OK][/light_green] {package} has been installed. (PKG-{counter:02d})")
    else:
        print(f"[OK] {package} has been installed. (PKG-{counter:02d})")
    counter += 1
