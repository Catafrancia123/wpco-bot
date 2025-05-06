""" Version 0.3.3:
    - New autoroles feature (WPCO only)
    - Self-Deployment is back (still no 4hr limit)
    - Event hosting and ping in dms (WIP & WPCO only.)
    - Autoroles for new members who joined."""

import discord, datetime, sys, os, asyncio, random, json, time
from discord.ext import commands
import playsound3 as playsound
from pathlib import Path
from rich import print as rprint
from rich.progress import Progress, BarColumn, TimeElapsedColumn, SpinnerColumn
from saveloader import edit_json, load_json, load_mongodb, edit_mongodb, find_save
#* install better comments on vscode for better comments!!

pymongo_installed = True
#? Do YOU have pymongo?
try:
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError:
    pymongo_installed = False

#! no touchy!!
if pymongo_installed:
    MONGO_URL = load_json("config.json", "databaseToken")
    db = AsyncIOMotorClient(MONGO_URL)

#* pyinstaller hotfix
def resource_path(relative_path):
    try: 
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def clear():
    if sys.platform.startswith(('win32')):
        os.system('cls')
    elif sys.platform.startswith(('linux', 'cygwin', 'darwin', 'freebsd')):
        os.system('clear')

async def help_bot(ctx):
    await ctx.reply("""```Humor Commands:
  wack            ow my head hurts - ai bot??
  wake_yassin    
  say             Make the bot say anything....
  shucks
  roll            Classic RNG command.
 
  Functional Commands:
  add_points      Add points to a member.
  check_password  Checks your current password
  help_s          Shows this message
  ping            Shows the bot's latency
  points          Get the number of points a user has/you have.     
  self_deploy     Used for logging Self-Deployments (Note: check description)
  setup           Setup in order to run the bot. (RUN THIS COMMAND USING /setup.)
  shutdown        Turns off the bot. (no need terminal killing)

Type /help_s command for more info on a command. (coming soon)
You can also type /help_s category for more info on a category. (coming soon)```""")

"""async def bot_timer(unix_target : int = 0):
    if unix_target == 0: 
        pass
    else:
        unix_now = datetime.datetime.now(datetime.timezone.utc).timestamp()
        timer = unix_target - unix_now
        tformat = datetime.datetime.utcfromtimestamp(timer).strftime("%A, %d-%m-%Y at %H:%M:%S UTC")

        if timer > 0:
            rprint(f"[[bright_yellow]WARNING[/bright_yellow]] Bot set for shutdown time: {tformat}")
            await asyncio.sleep(timer)  
            await bot.close()
        else:
            rprint("[[bright_red]ERROR[/bright_red]] The target shutdown time has already passed.")"""

BOTVER = "0.3.3"
RUN_ON_SERVER = load_json("config.json", "run_bot_on", "settings")
SAVE_FILE = f"save_{RUN_ON_SERVER}.json"
EVENTS = {1: "Deployment", 2: "Basic Training", 3: "Combat Training"}
WPCO_ROLE = [1207498264644157521]
GOC_ROLE = [989415158549995540]
COMBINED_ROLES = WPCO_ROLE + GOC_ROLE
ADMIN_ROLES = (1345327248265449502, 1207383065270419528, 1224066316990812272, 1179524589592784996, 1349692227223289896, 1244197639331774556, 1351470675013013574)
deployment_id = bot_reset = 0
RANKS = {"EnO" : "Enlisted Operative", "O" : "Operative", "SnO" : "Senior Operative", "ElO" : "Elite Operative", "SpC" : "Specialist", "LnC" : "Lance Corporal", # Low ranking
         "SgT" : "Sergeant", "SsT" : "Staff Sergeant", "SfC" : "Sergeant First Class", "OfC" : "Officer", "SnO" : "Senior Officer", "VnO" : "Veteran Officer", "CfO" : "Chief Officer", # Medium ranking
         "2LT" : "2nd Lieutenant", "1LT" : "1st Lieutenant", "CpT" : "Captain", "MaJ" : "Major", "C" : "Colonel", "M" : "Marshal", "MG" : "Major General", "GeN" : "General"} # High ranking
clear()

#* Setup
class Bot(commands.Bot):
    def __init__(self):
        #* I HAVE THE POWER OF EVERYTHING!  
        global intents
        intents = discord.Intents.default()
        intents.message_content = True #! see message content
        intents.members = True #! see members
        intents.reactions = True #! see reactions

        super().__init__(command_prefix = "$", intents = intents)

    def __str__() -> str:
        return "Bot Class, please dont print this!!"

    async def on_command_error(self, ctx, error):
        rprint(f'[[bright_red]ERROR[/bright_red]]', error)
        await ctx.reply(f"{error}")

    def is_registered(self) -> any:
        async def predicate(ctx) -> bool:
            user = ctx.author
            try: 
                load_json(SAVE_FILE, user.name, "user_data")
                return True
            except KeyError: 
                return False
        return commands.check(predicate)
    
    def is_blacklisted(self) -> any:
        async def predicate_bl(ctx) -> bool:
            user = ctx.author
            BLACKLIST_ROLES = (1303267805411545098, 1349692227223289896)
            role = discord.utils.find(lambda r: r.id in BLACKLIST_ROLES, ctx.message.guild.roles)

            if role in user.roles:
                await ctx.reply(f"You have been banned from the bot. \nIf you think this was a mistake, Please contact catamapp/lightningstormyt.")
                return False
            else:
                return True
        return commands.check(predicate_bl)
    
    def make_error_embed(self, user : str, error_code : int = 99, error_msg : str = None) -> discord.Embed:
        time_format = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), "Today at %I:%M %p UTC.")
        #* add more later!!
        errors = {1:"Command not found/doesn't exist.", 
                2:"An input is missing, please try again.",
                3:"An input is invalid/unprocessable.",
                4:"You don't have permission to run this command.",
                5:"Server Error. Either from API or Discord.",
                6:"You must run `/setup` before running any commands. Its necessary for the bot to run.\nIf you already done ``/setup`` and this shows up, please ping catamapp or lightningstormyt ASAP.",
                7:"Bot doesn't have permission to do the following action, ping catamapp or lightningstormyt ASAP.",
                8:"Command didn't register properly, ping catamapp or lightningstormyt ASAP.",
                9:"Intents not properly enabled, ping catamapp or lightningstormyt ASAP.",
                10:"Connection with Discord failed, please try again later.",
                11:"Connection with Discord failed, please try again later.", 
                12:"Connection with Discord failed, please try again later.", 
                13:"MongoDB raised a exception, ping catamapp ASAP.",
                99:f"Unknown Error, please ping catamapp/lightningstormyt ASAP. (ERR ??)\nError Message: {error_msg}\n(IF THIS IS A KEY ERROR IGNORE.)"}

        embedvar = discord.Embed(
            title=f"Error {error_code:02d}",
            description=f"{errors[error_code]}",
            color=discord.Color.red(),
        )
        embedvar.set_footer(text=time_format)
        embedvar.set_thumbnail(url="attachment://WPCO.png")
        if error_code != 99:
            print(f"ERR {error_code:02d}: {time_format} by {user}")

        return embedvar
    
    async def startup_progressbar(self):
        with Progress(
        "[progress.description]{task.description}",
        SpinnerColumn(),
        BarColumn(),
        TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("[cyan]Starting up...[/cyan]", total=100)

            for i in range(6):  
                progress.update(task, advance=10)
                time.sleep(0.16)

            progress.update(task, completed=100)
            rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[light_green]COMPLETE[/light_green]] Bot has completed startup and now can be used.')

class UIInput_Events(discord.ui.Modal):
    def __init__(self, title="Event Forum"):
        self.host = discord.ui.TextInput(label="Host", placeholder="Enter host name...", required=True)
        self.co_host = discord.ui.TextInput(label="Co-Host", placeholder="Enter co-host name...", required=True)
        self.supervisor = discord.ui.TextInput(label="Supervisor", placeholder="Enter supervisor name...", required=True)
        self.type = 1

    async def on_submit(self, ctx):
        time_format = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), "Today at %I:%M %p UTC.")
        event_channel = discord.utils.get(ctx.guild.text_channels, name="》events")
        if not event_channel:
            raise Exception("Channel not Found.")
        
        embedvar = discord.Embed(
            title=EVENTS[self.type],
            description=f"Host: {self.host.value}\nCo-host: {self.co_host.value}\nSupervisor: {self.supervisor.value}",
            color=discord.Color.blue
        )
        embedvar.set_footer(text=time_format)
        embedvar.set_thumbnail(url="attachment://WPCO.png")

        #await event_channel.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=embedvar)
        await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=embedvar)
        await ctx.send(f"Event {EVENTS[self.type]} Created.", ephemeral=True)
    
bot = Bot()

#* Command Prompt 
async def command_prompt(ctx):
    unix = int(datetime.datetime.now().timestamp())
    print("\n")
    while True:
        inp = str(input(f'{load_json("config.json", "run_bot_on", "settings")}-bot> '))
        if inp == "shutdown":
            await ctx.reply(f"Bot shutdown initiated by **COMMAND** at: <t:{unix}:F> (EVN 02)")
            rprint(f"[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[bright_yellow]WARNING[/bright_yellow]] Bot shutdown initiated by you!!")
            await bot.close()

#* Humor Commands
@bot.hybrid_command(with_app_command = True, brief = "uhh my head hurts")
@bot.is_blacklisted()
@commands.has_any_role(*COMBINED_ROLES)
async def wack(ctx):
    await ctx.reply("uhh my head hurts\n- wpco ai bot")

@bot.hybrid_command(with_app_command=True, brief="embed testing.")
@bot.is_blacklisted()
@commands.has_any_role(*ADMIN_ROLES)
async def test_embed(ctx):
    embedvar = discord.Embed(
        title="martin is a goober?",
        description="maybe",
        url="https://catafrancia123.github.io/catamapp-website/",
        color=discord.Color.blue(),
    )
    embedvar.set_footer(text="hi im shingmans developing this")
    img = discord.File("images/shingmans.png", filename="shingmans.png")
    embedvar.set_thumbnail(url="attachment://shingmans.png")

    await ctx.reply(file=img, embed=embedvar)

@bot.hybrid_command(with_app_command = True)
@bot.is_blacklisted()
@commands.has_any_role(*ADMIN_ROLES)
async def wake_yassin(ctx):
    await ctx.reply("<@956699005960720474> wake up")

@bot.hybrid_command(with_app_command = True, brief = "martin command")
@bot.is_blacklisted()
@commands.has_any_role(*COMBINED_ROLES)
async def shucks(ctx):
    await ctx.reply("https://cdn.discordapp.com/attachments/1207383289225281606/1328003148224139355/youtube-ugfghba-rBs.mp4?ex=67851ecf&is=6783cd4f&hm=ac276199166ddcee99252fd3d85f4ecbe4c24343104254e003cae82e8ee154ee&    ")

#TODO: delete user messsage if sent with "$", else run command normally.
@bot.hybrid_command(with_app_command = True, brief = "Make the bot say anything!")
@bot.is_blacklisted()
@commands.has_any_role(*COMBINED_ROLES)
async def say(ctx, *, text):
    if ctx.prefix:
        await ctx.message.delete()
    await ctx.send(str(text))

@bot.hybrid_command(with_app_command = True, brief = "Classic RNG command.")
@bot.is_blacklisted()
@commands.has_any_role(*COMBINED_ROLES)
async def roll(ctx, end_num: int, hide: bool = False):
    await ctx.reply(f":game_die: Rolled Number: {random.randint(1, end_num)}", ephemeral=hide)

#* Functional Commands
@bot.hybrid_command(with_app_command = True, brief = "Checks bot ping.")
@commands.has_any_role(*COMBINED_ROLES)
async def ping(ctx):
    time_format = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), "Today at %I:%M %p UTC.")
    ping = bot.latency
    embedvar = discord.Embed(
        title="Pong!",
        description=f"Bot latency: {int(ping*1000)}ms",
        color=discord.Color.blue(),)
    embedvar.set_footer(text=time_format)
    embedvar.set_thumbnail(url="attachment://WPCO.png")

    await ctx.reply(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=embedvar)
    
@bot.hybrid_command(with_app_command = True, brief = "shutdowns the bot lmao")
@bot.is_registered()
@bot.is_blacklisted()
@commands.has_any_role(*ADMIN_ROLES)
async def shutdown(ctx, password: str):
    user = ctx.author
    unix = int(datetime.datetime.now().timestamp())

    if password == load_json(SAVE_FILE, user.name, "user_data"):
        await ctx.reply(f"Bot shutdown initiated by **{user.name}** at: <t:{unix}:F> (EVN 01)")
        rprint(f"[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[bright_yellow]WARNING[/bright_yellow]] Bot shutdown initiated by {user.name}.")
        await bot.close()
    else:
        await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=bot.make_error_embed(user.name, 3))

# TODO: add 4 hour limit (suggested by tamago) / 7 hour limit (handbook)
@bot.hybrid_command(with_app_command = True, brief = "Used for logging Self-Deployments (USE THE CODES IN THE DESCRIPTION)", description = "S = start, P = pause, UP = unpause,  E = end")
@bot.is_registered()
@bot.is_blacklisted()
@commands.has_any_role(*WPCO_ROLE)
async def self_deploy(ctx, status: str):
    global start, paused_at, total_paused_time, deployment_id, deployment_text, unix_start, g_user
    g_user = ctx.author
    user = ctx.author
    safe_name = "".join(c for c in user.name if c.isalnum() or c in "-_")

    if "start" not in globals():
        start = 0
    if "paused_at" not in globals():
        paused_at = 0
    if "total_paused_time" not in globals():
        total_paused_time = 0
    if "deployment_id" not in globals():
        deployment_id = 0

    if status.upper() == "S":
        deployment_id += 1
        start = time.time()
        unix_start = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        deployment_text = datetime.datetime.now(datetime.timezone.utc).strftime("deployment_%d_%m_%Y")
        time_format = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), "Today at %I:%M %p UTC.")
        embedvar = discord.Embed(
            title="Self-Deployment Started",
            description=f"Operative: {user.name}\nStarted at: <t:{unix_start}:F>",
            color=discord.Color.green(),)
        embedvar.set_footer(text=f"Shift ID: {deployment_text}_{deployment_id} | {time_format}")
        embedvar.set_thumbnail(url="attachment://WPCO.png")
        edit_json(f"./selfdep/{safe_name}.json", f"{deployment_text}_{deployment_id}_unix_start", unix_start, "deployment_unix")
        await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=embedvar)
    elif status.upper() == "P":
        if paused_at == 0:
            paused_at = time.time()
            unix_pause = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            elapsed_time = datetime.timedelta(seconds=int(paused_at - start - total_paused_time))
            time_format = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), "Today at %I:%M %p UTC.")
            embedvar = discord.Embed(
                title="Self-Deployment Paused",
                description=f"Operative: {user.name}\nPaused at: <t:{unix_pause}:F>\nElapsed time: {elapsed_time}",
                color=discord.Color.yellow(),)
            embedvar.set_footer(text=f"Shift ID: {deployment_text}_{deployment_id} | {time_format}")
            embedvar.set_thumbnail(url="attachment://WPCO.png")
            await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=embedvar)
        else:
            await ctx.reply("The deployment is already paused.", ephemeral=True)
    elif status.upper() == "UP":
        # wake up boi
        if paused_at != 0:
            paused_duration = time.time() - paused_at
            total_paused_time += paused_duration
            paused_at = 0
            unix_unpause = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            elapsed_time = datetime.timedelta(seconds=int(time.time() - start - total_paused_time))
            time_format = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), "Today at %I:%M %p UTC.")
            embedvar = discord.Embed(
                title="Self-Deployment Unpaused",
                description=f"Operative: {user.name}\nUnpaused at: <t:{unix_unpause}:F>\nElapsed time: {elapsed_time}",
                color=discord.Color.yellow(),)
            embedvar.set_footer(text=f"Shift ID: {deployment_text}_{deployment_id} | {time_format}")
            embedvar.set_thumbnail(url="attachment://WPCO.png")
            await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=embedvar)
        else:
            await ctx.reply("The deployment is not paused.", ephemeral=True)
    elif status.upper() == "E":
        end = time.time()
        try:
            total_time = end - start - total_paused_time
            unix_end = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            elapsed_time = datetime.timedelta(seconds=int(total_time))
            time_format = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), "Today at %I:%M %p UTC.")
            embedvar = discord.Embed(
                title="Self-Deployment Ended",
                description=f"Operative: {user.name}\nEnded at: <t:{unix_end}:F>\nElapsed time: {elapsed_time}",
                color=discord.Color.red(),)
            embedvar.set_footer(text=f"Shift ID: {deployment_text}_{deployment_id} | {time_format}")
            embedvar.set_thumbnail(url="attachment://WPCO.png")
            edit_json(f"./selfdep/{safe_name}.json", f"{deployment_text}_{deployment_id}_time_seconds", int(total_time), "deployments")
            await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=embedvar)
        except NameError:
            await ctx.reply("You did not start a deployment yet.", ephemeral=True)
        
@bot.hybrid_command(with_app_command = True, brief = "Add points to a member.", help = "Add points to a member. (put a negative infront if you want to remove points)")
@bot.is_registered()
@bot.is_blacklisted()
@commands.has_any_role(*ADMIN_ROLES)
async def add_points(ctx, points: int, to_user: discord.Member, password: str):
    user = ctx.author
    embedvar = discord.Embed(title="Error 07",description=f"**{user.name}** has not registered yet. (ERR 07)\nPlease tell **{user.name}** to run command ``/setup``, then try again.",color=discord.Color.red(),)
    time = datetime.datetime.now(datetime.timezone.utc)
    time_format = datetime.datetime.strftime(time, "Today at %I:%M %p UTC.")
     
    if password == load_json(SAVE_FILE, user.name, "user_data"):
        edit_json(SAVE_FILE, f"{to_user.name}_pts", int(load_json(SAVE_FILE, f"{to_user.name}_pts", "points"))+points, "points")

    try:
        embedvar = discord.Embed(
		title=f"Amount of added points for {to_user.name}:",
		description=f"**{to_user.name}**'s total points: {load_json(SAVE_FILE, f'{to_user.name}_pts', 'points')}\nAdded by **{user.name}**",
		color=discord.Color.blue(),)
    except KeyError:
        print(f"ERR 07: {time_format} by {user.name}")
        
    embedvar.set_footer(text=time_format)
    embedvar.set_thumbnail(url="attachment://WPCO.png")
    await ctx.reply(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=embedvar)

@bot.hybrid_command(with_app_command = True, brief = "Get the number of points a user has/you have.")
@bot.is_registered()
@bot.is_blacklisted()
@commands.has_any_role(*COMBINED_ROLES)
async def points(ctx, user: discord.Member):
    embedvar = discord.Embed(title="Error 07",description=f"**{user.name}** has not registered yet. (ERR 07)\nPlease tell **{user.name}** to run command ``/setup``, then try again.",color=discord.Color.red(),)
    time = datetime.datetime.now(datetime.timezone.utc)
    time_format = time.strftime("Today at %I:%M %p UTC.")
    try:
        embedvar = discord.Embed(
		title=f"Amount of points for {user.name}:",
		description=f"Total points: {load_json(SAVE_FILE, f'{user.name}_pts', 'points')}",
		color=discord.Color.blue(),)
    except KeyError:
        print(f"ERR 07: {time_format} by {user.name}")
    
    embedvar.set_footer(text=time_format)
    embedvar.set_thumbnail(url="attachment://WPCO.png")
    await ctx.reply(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=embedvar)

@bot.hybrid_command(with_app_command = True, brief = "Setup in order to run the bot. (RUN THIS COMMAND USING /setup.)")
@bot.is_blacklisted()
@commands.has_any_role(*COMBINED_ROLES)
async def setup(ctx, password: str):
    collection = db[f"save_{RUN_ON_SERVER}"]["save_file"]
    user = ctx.author
    safe_name = "".join(c for c in user.name if c.isalnum() or c in "-_")
    selfdep_file = Path(f"./selfdep/{safe_name}.json")
    user_count = load_json(SAVE_FILE, "user_count")

    if len(password) < 8:
        await ctx.reply(":warning: You need a minimal of 8 characters for your password.", ephemeral=True)
    elif len(password) >= 8:
        try:
            load_json(SAVE_FILE, user.name, "user_data")
            load_mongodb(collection, user.name, index=user_count)
            await ctx.reply(":warning: You have already done setup.", ephemeral=True)
        except KeyError:
            edit_json(SAVE_FILE, user.name, password, "user_data")
            edit_json(SAVE_FILE, f"{user.name}_pts", 0, "points")
            if pymongo_installed:
                try:
                    edit_mongodb(collection, user.name, password, index=user_count)
                    edit_mongodb(collection, f"{user.name}_pts", 0, index=user_count)
                except Exception:
                    await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=bot.make_error_embed(user.name,13))
            if RUN_ON_SERVER == "wpco":
                if selfdep_file.is_file():
                    pass
                else:
                    template = {
                        "id" : user.id, 
                        "deployments": {}, 
                        "deployment_unix": {}
                    }

                    with open(f"./selfdep/{safe_name}.json", mode="w", encoding="utf-8") as outfile: 
                        json.dump(template, outfile)
                    if pymongo_installed:
                        try:
                            save_dir = db[f"save-{RUN_ON_SERVER}"]
                            save_file = save_dir[f"{user.name}_dep"]
                            save_file.insert_one(template)
                        except Exception:
                            await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=bot.make_error_embed(user.name,13))
            user_count += 1
            edit_json(SAVE_FILE, "user_count", user_count)        
            await ctx.reply(":white_check_mark: Setup complete. You may use the bot now.", ephemeral=True)

@bot.hybrid_command(with_app_command = True, brief = "Checks your password. if you forgot it, dm catamapp")
@commands.has_any_role(*COMBINED_ROLES)
@bot.is_registered()
@bot.is_blacklisted()
async def check_password(ctx, password: str):
    #* thx plate
    user = ctx.author

    if password == load_json(SAVE_FILE, user.name, "user_data"):
        await ctx.reply(":white_check_mark: Password is **correct**.", ephemeral=True)
    else:
        await ctx.reply(":x: Password is **incorrect**, try again.", ephemeral=True)

@bot.hybrid_command(with_app_command = True, brief = "Basic Help Command")
@commands.has_any_role(*COMBINED_ROLES)
@bot.is_blacklisted()
async def help_s(ctx):
    await ctx.reply("""```Humor Commands:
  wack            ow my head hurts - ai bot??
  wake_yassin    
  say             Make the bot say anything....
  shucks
  roll            Classic RNG command.
 
  Functional Commands:
  add_points      Add points to a member.
  check_password  Checks your current password
  help_s          Shows this message
  ping            Shows the bot's latency
  points          Get the number of points a user has/you have.     
  self_deploy     Used for logging Self-Deployments (Note: check description)
  setup           Setup in order to run the bot. (RUN THIS COMMAND USING /setup.)
  shutdown        Turns off the bot. (no need terminal killing)

Type /help_s command for more info on a command. (coming soon)
You can also type /help_s category for more info on a category. (coming soon)```""")
    
@bot.hybrid_command(with_app_command = True, brief = "Read the description for the event codes.", description="1: Deployment, 2: Basic Training, 3: Combat Training")
@commands.has_any_role(*ADMIN_ROLES)
@bot.is_blacklisted()
@bot.is_registered()
async def start_event(interaction: discord.Interaction, event: int):
    uiinput = UIInput_Events()
    uiinput.type = event
    await interaction.response.send_modal(uiinput)

@bot.hybrid_command(with_app_command = True, brief = "Adds a member to the faction. (WPCO ONLY.)")
@commands.has_any_role(*ADMIN_ROLES)
@bot.is_blacklisted()
@bot.is_registered()
async def add_member(ctx, user: discord.Member):
    role = ctx.guild.get_role(WPCO_ROLE[0])
    if role is None:
        raise Exception("Role not found.")
    
    if role not in user.roles:
        await user.add_roles(role, reason=f"Welcome to WPCO, {user.name}!")
        await ctx.send(f"{user.name} added as a member, please welcome him.", ephemeral=True)
    else:
        await ctx.send(f"{user.name} has already been a member.", ephemeral=True)

@bot.hybrid_command(with_app_command = True, brief = "Syncs the bot...")
@commands.has_any_role(*ADMIN_ROLES)
@bot.is_blacklisted()
@bot.is_registered()
async def sync(ctx):
    await bot.setup_hook()
    await ctx.send(":white_check_mark: Bot successfully synced.")

#* Events
@bot.event
async def on_ready():
    global bot_reset
    if bot_reset == 0:
        await bot.load_extension("jishaku")
    bot_reset += 1
    #! asyncio stupid, fix this
    await asyncio.to_thread(bot.startup_progressbar)
    rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[light_green]SUCCESSFUL[/light_green]] Synced slash commands and loaded jishaku.')
    rprint(f"[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[light_green]VERSION[/light_green]] Discord.py version [bright_yellow]{discord.__version__}[/bright_yellow], Bot version [bright_yellow]{BOTVER}[/bright_yellow]")
    rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[light_green]SUCCESSFUL[/light_green]] Logged in as [blue]{bot.user}[/blue] (ID: [#cccccc]{bot.user.id}[/#cccccc])')
    if not pymongo_installed:
        rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[bright_red]ERROR[/bright_red]] pymongo not found, using alternative save files.')
        find_save("json")
    else:
        try:
            client = AsyncIOMotorClient(MONGO_URL)
            await client.admin.command('ping')  # Test MongoDB connection
            find_save("mongodb")
            rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[light_green]SUCCESSFUL[/light_green]] MongoDB successfully connected.')
        except Exception:
            rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[bright_red]ERROR[/bright_red]] MongoDB failed to connect.')
    #wait(1)
    #timer_input = int(input("Set automatic bot shutdown time in unix value (leave empty if manual shutdown): "))
    #await bot_timer(timer_input)
    rprint(f"[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[bright_yellow]WARNING[/bright_yellow]] Please ping catamapp/lightningstormyt for bot maintenance/unhandled errors.")
    rprint(f'[grey]{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/grey] [[light_green]COMPLETE[/light_green]] Bot has completed startup and now can be used.')
    try:
        await asyncio.to_thread(playsound.playsound, "sounds/beep.wav")
    except Exception as e:
        pass
    #TODO: fix this
    #await asyncio.to_thread(command_prompt)

@bot.event
async def on_member_join(user):
    if user.guild.id == 1207335443608113152:
        roles = [1213355943690117140, 1207670421252476928, 1356518786068381796, 1213354335195365396]
        for i in roles:
            role = user.guild.get_role(i)
            await user.add_roles(role, reason=f"{user.name} joined the server.")

AUTOROLES_REACTIONS = {"Event": 1214531847959089173,
                       "Poll": 1214531713602945044,
                       "QuestionMark": 1214532032974295040,
                       "scroll": 1214532211035078726,
                       "Announcement": 1214051280897712168,
                       "warning": 1358721097867989255}
AUTOROLE_IDS = (881922017887154226, 751049879630905345)
@bot.event
async def on_raw_reaction_add(reaction):
    guild = bot.get_guild(1207335443608113152)
    local_emoji = reaction.emoji
    user = guild.get_member(reaction.user_id)
    if reaction.message_author_id in AUTOROLE_IDS and reaction.channel_id == 1217864965587861675:
        print(f"User: {user.name}, Emoji: {local_emoji.name}")
        user.add_roles(AUTOROLES_REACTIONS[local_emoji.name], reason="Added role via autoroles")

@bot.event
async def on_raw_reaction_remove(reaction):
    #* manual fetching haiyaa (reaction.message_author_id doesn't work in this event!!!
    guild = bot.get_guild(1207335443608113152)
    local_emoji = reaction.emoji
    user = guild.get_member(reaction.user_id)
    channel = guild.get_channel(reaction.channel_id)
    message = await channel.fetch_message(reaction.message_id)
    author = message.author

    if author.id in AUTOROLE_IDS and reaction.channel_id == 1217864965587861675:
        print(f"User: {user.name}, Removed Emoji: {local_emoji.name}")
        user.remove_roles(AUTOROLES_REACTIONS[local_emoji.name], reason="Removed role via autoroles")

# TODO: fix this
"""@bot.event
async def on_message(ctx):
    now = datetime.datetime.now(datetime.timezone.utc)
    hour4 = now.hour + 4
    if hour4 == 24: hour4 = 0
    elif hour4 == 25: hour4 = 1
    elif hour4 == 26: hour4 = 2
    try: safe_name = "".join(c for c in g_user.name if c.isalnum() or c in "-_")
    except NameError: print("name_error")
    unix = int(datetime.datetime(now.year, now.month, now.day, hour4, now.minute, now.second).timestamp())

    try: data = load_json(f"./selfdep/{safe_name}.json", f"{deployment_text}_{deployment_id}_unix_start", "deployment_unix")
    except KeyError: print("key_error")

    try:
        if data >= unix:
            await ctx.reply(f"<@{g_user.id}>, Take care of yourself, its been 4 hours! (or you just forgot to end the self-dep :rofl:)")
    except NameError: print("name_error")"""

@bot.event
async def on_command_error(ctx, error):
    user = ctx.author
    time = datetime.datetime.now()
    time_format = time.strftime('%A, %d %B %Y, %I:%M %p') 
    if isinstance(error, commands.CommandNotFound):
        #! command not found
        await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=bot.make_error_embed(user.name,1))
    elif isinstance(error, commands.MissingRequiredArgument):
        #! no input
        await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=bot.make_error_embed(user.name,2))
    elif isinstance(error, commands.BadArgument):
        #! input not valid/wrong
        await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=bot.make_error_embed(user.name,3))
    elif isinstance(error, commands.MissingAnyRole):
        #! no perms?
        await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=bot.make_error_embed(user.name,4))
    elif isinstance(error, discord.HTTPException):
        #! discord.py error
        await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=bot.make_error_embed(user.name,5))
    elif isinstance(error, commands.CheckFailure):
        #! not registered
        await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=bot.make_error_embed(user.name,6))
    elif isinstance(error, discord.Forbidden):
        #! bot doesnt have perms to do an action
        await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=bot.make_error_embed(user.name,7))
    elif isinstance(error, commands.CommandRegistrationError):
        #! command registration failed
        await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=bot.make_error_embed(user.name,8))
    elif isinstance(error, discord.PrivilegedIntentsRequired):
        #! intents not properly enabled
        await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=bot.make_error_embed(user.name,9))
    elif isinstance(error, discord.ConnectionClosed):
        #! connection with discord closed
        await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=bot.make_error_embed(user.name,10))
    elif isinstance(error, discord.GatewayNotFound):
        #! connection with discord gateaway failed
        await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=bot.make_error_embed(user.name,11))
    elif isinstance(error, discord.NotFound):
        #! 404 not found
        await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=bot.make_error_embed(user.name,12))
    else:
        #! what happen?? (python error or smth)
        rprint(f"[[bright_red]ERROR[/bright_red]] Unknown error: {error}\n{time_format}")
        await ctx.send(file=discord.File("images/WPCO.png", filename="WPCO.png"), embed=bot.make_error_embed(user.name,error_msg=error))

if __name__ == "__main__":
    bot.run(load_json("config.json", "token"))