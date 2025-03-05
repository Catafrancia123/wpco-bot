import subprocess, sys, os
packages = ["discord.py", "rich", "playsound3", "pymango"]

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

for i in packages:
    subprocess.run([sys.executable, "-m", "pip", "install", i,  "--quiet", "-U"]) 
    print(f"[OK] {i} has been installed.")

