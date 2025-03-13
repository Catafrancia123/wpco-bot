import discord, datetime, sys, os, asyncio
import discord.gateway
import playsound3 as playsound
from rich import print as rprint
from discord.ext import commands
from saveloader import *
#* install better comments on vscode for better comments!!

pymongo_installed = True
#? Do YOU have pymongo?
try:
    from pymongo import MongoClient
except ImportError:
    pymongo_installed = False

#! no touchy!!
if pymongo_installed:
    MONGO_URL = load_json("config.json", "databaseToken")
logo = discord.File("images/WPCO.png", filename="WPCO.png")

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

def is_blacklisted():
    async def predicate_bl(ctx):
        user = ctx.author
        BLACKLIST_ROLES = (1303267805411545098, 1349692227223289896)
        role = discord.utils.find(lambda r: r.id in BLACKLIST_ROLES, ctx.message.guild.roles)

        if role in user.roles:
            await ctx.reply(f"You have been banned from the bot. \nIf you think this was a mistake, Please contact catamapp/yassin1234.")
            return False
        else:
            return True
    return commands.check(predicate_bl)

def is_registered():
    async def predicate(ctx):
        user = ctx.author
        try: 
            load_json("save_wpco.json", user.name, "user_data")
            return True
        except KeyError: 
            return False
    return commands.check(predicate)

def make_error_embed(error_code : int = 99, error_msg : str = None):
	time_format = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), "Today at %I:%M %p UTC.")
	#* add more later!!
	errors = {1: "Command not found/doesn't exist.", 
              2:"An input is missing, please try again.",
              3:"An input is invalid/unprocessable.",
              4:"You don't have permission to run this command.",
              5:"Server Error. Either from API or Discord.",
              6:"You must run ``/setup`` before running any commands. Its necessary for the bot to run.\nIf you already done ``/setup`` and this shows up, please ping catamapp or yassin1234 ASAP.",
              7:"Bot doesn't have permission to do the following action. Ping catamapp or yassin1234 ASAP.",
              8:"Command didn't register properly. Ping catamapp or yassin1234 ASAP.",
              9:"Intents not properly enabled. Ping catamapp or yassin1234 ASAP.",
              10:"Connection with Discord failed. Please try again later.",
              11:"Connection with Discord failed. Please try again later.", 
              99:f"Unknown Error. Please ping catamapp/yassin1234 ASAP. (ERR ??)\nError Message: {error_msg}\n(IF THIS IS A KEY ERROR IGNORE.)"}

	embedvar = discord.Embed (
	    title=f"Error {error_code:02d}",
	    description=f"{errors[error_code]}",
	    color=discord.Color.red(),
	)
	embedvar.set_footer(text=time_format)
	embedvar.set_thumbnail(url="attachment://WPCO.png")

	return embedvar

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
            print("[[bright_red]ERROR[/bright_red]] The target shutdown time has already passed.")"""

EVENTS = ("Deployment", "Training", "Tryout", "Supervision")
ROLES = (1288801886706860082, 1207498264644157521, 1297825813567377449, 989415158549995540) 
ADMIN_ROLES = (1288801886706860082, 1272839552314118306, 1345327248265449502, 1207383065270419528, 1224066316990812272, 1179524589592784996, 1349692227223289896, 1244197639331774556)
deployment_id = 0
RANKS = {"EnO" : "Enlisted Operative", "O" : "Operative", "SnO" : "Senior Operative", "ElO" : "Elite Operative", "SpC" : "Specialist", "LnC" : "Lance Corporal", # Low ranking
         "SgT" : "Sergeant", "SsT" : "Staff Sergeant", "SfC" : "Sergeant First Class", "OfC" : "Officer", "SnO" : "Senior Officer", "VnO" : "Veteran Officer", "CfO" : "Chief Officer", # Medium ranking
         "2LT" : "2nd Lieutenant", "1LT" : "1st Lieutenant", "CpT" : "Captain", "MaJ" : "Major", "C" : "Colonel", "M" : "Marshal", "MG" : "Major General", "GeN" : "General"} # High ranking
BOTVER = "0.3.2" 
#* GOC using this bot and removal of rank promotion (they're manual!!). still will save the ranks const file for future use.
clear()

# Setup
class Bot(commands.Bot):
    def __init__(self):
        global intents
        intents = discord.Intents.default()

        #* Permissions
        intents.members = True # see members
        intents.message_content = True # see messages
        intents.reactions = True # see reactions
        super().__init__(command_prefix = "$", intents = intents)

    async def on_command_error(self, ctx, error):
        rprint(f'[[bright_red]ERROR[/bright_red]]', error)
        await ctx.reply(f"{error}")

bot = Bot()
client = discord.Client(intents=intents)

#* Humor Commands
@bot.hybrid_command(with_app_command = True, brief = "uhh my head hurts")
@is_blacklisted()
@commands.has_any_role(*ROLES)
async def wack(ctx):
    await ctx.reply("uhh my head hurts\n- wpco ai bot")

@bot.hybrid_command(with_app_command=True, brief="embed testing.")
@is_blacklisted()
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
@is_blacklisted()
@commands.has_any_role(*ADMIN_ROLES)
async def wake_yassin(ctx):
    await ctx.reply("<@956699005960720474> wake up")

@bot.hybrid_command(with_app_command = True, brief = "martin command")
@is_blacklisted()
@commands.has_any_role(*ROLES)
async def shucks(ctx):
    await ctx.reply("https://cdn.discordapp.com/attachments/1207383289225281606/1328003148224139355/youtube-ugfghba-rBs.mp4?ex=67851ecf&is=6783cd4f&hm=ac276199166ddcee99252fd3d85f4ecbe4c24343104254e003cae82e8ee154ee&    ")

@bot.hybrid_command(with_app_command = True, brief = "Make the bot say anything!")
@is_blacklisted()
@commands.has_any_role(*ROLES)
async def say(ctx, *, message):
    await ctx.reply(str(message))

#* Functional Commands
@bot.hybrid_command(with_app_command = True, brief = "Checks bot ping.")
@commands.has_any_role(*ROLES)
async def ping(ctx):
    time_format = datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), "Today at %I:%M %p UTC.")
    ping = bot.latency
    embedvar = discord.Embed(
        title="Pong!",
        description=f"Bot latency: {int(ping*1000)}ms",
        color=discord.Color.blue(),)
    embedvar.set_footer(text=time_format)
    embedvar.set_thumbnail(url="attachment://WPCO.png")

    await ctx.reply(file=logo, embed=embedvar)
    
@bot.hybrid_command(with_app_command = True, brief = "shutdowns the bot lmao")
@is_registered()
@is_blacklisted()
@commands.has_any_role(*ADMIN_ROLES)
async def shutdown(ctx, password : str):
    user = ctx.author
    unix = int(datetime.datetime.now().timestamp())

    if password == load_json("save_wpco.json", user.name, "user_data"):
        await ctx.reply(f"Bot shutdown initiated by **{user.name}** at: <t:{unix}:F> (EVN 01)")
        await bot.close()
    else:
        await ctx.reply("https://tenor.com/view/noperms-gif-27260516")

# TODO: fix this
"""@bot.hybrid_command(with_app_command = True, brief = "Used for logging Self-Deployments (USE THE CODES IN THE DESCRIPTION)", description = "S = start, P = pause, UP = unpause,  E = end")
@is_registered()
@commands.has_any_role(*ROLES)
async def self_deploy(ctx, status: str):
    global start, paused_at, total_paused_time, deployment_id, deployment_text, unix_start, g_user
    g_user = ctx.author
    user = ctx.author
    safe_name = "".join(c for c in user.name if c.isalnum() or c in "-_")

    if user.id in BLACKLIST_LIST:
        await ctx.reply(f"You have been banned from the bot for: {BLACKLIST_LIST[user.id]} \nIf you think this was a mistake, Please contact catamapp/yassin1234.")
    else: pass
    
    if "start" not in globals():
        start = 0
    if "paused_at" not in globals():
        paused_at = 0
    if "total_paused_time" not in globals():
        total_paused_time = 0
    if "deployment_id" not in globals():
        deployment_id = 0

    if status.upper() == "S":
        start = time.time()
        unix_start = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        deployment_text = datetime.datetime.now(datetime.timezone.utc).strftime("deployment_%d_%m_%Y")
        deployment_id += 1
        edit_json(f"./selfdep/{safe_name}.json", f"{deployment_text}_{deployment_id}_unix_start", unix_start, "deployment_unix")
        await ctx.reply(f"Started Self-Deployment for {user.name}. Started at: <t:{unix_start}:F>") 
    elif status.upper() == "P":
        if paused_at == 0:
            paused_at = time.time()
            unix_pause = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            elapsed_time = datetime.timedelta(seconds=int(paused_at - start - total_paused_time))
            await ctx.reply(f"Paused Self-Deployment for {user.name}. Paused at: <t:{unix_pause}:F>\nElapsed time: {elapsed_time}")
        else:
            await ctx.reply("The deployment is already paused!")
    elif status.upper() == "UP":
        # wake up boi
        if paused_at != 0:
            paused_duration = time.time() - paused_at
            total_paused_time += paused_duration
            paused_at = 0
            unix_unpause = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            elapsed_time = datetime.timedelta(seconds=int(time.time() - start - total_paused_time))
            await ctx.reply(f"Unpaused Self-Deployment for {user.name}. Unpaused at: <t:{unix_unpause}:F>\nElapsed time: {elapsed_time}")
        else:
            await ctx.reply("The deployment is not paused!")
    elif status.upper() == "E":
        end = time.time()
        try:
            total_time = end - start - total_paused_time
            unix_end = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            elapsed_time = datetime.timedelta(seconds=int(total_time))

            edit_json(f"./selfdep/{safe_name}.json", f"{deployment_text}_{deployment_id}_time_seconds", int(total_time), "deployments")
            await ctx.reply(f"Ended Self-Deployment for {user.name}. Ended at: <t:{unix_end}:F>\nTotal deployment time: {elapsed_time}")
        except NameError:
            await ctx.reply("You did not start a deployment yet.")"""
        
@bot.hybrid_command(with_app_command = True, brief = "Add points to a member.", help = "Add points to a member. (put a negative infront if you want to remove points)")
@is_registered()
@is_blacklisted()
@commands.has_any_role(*ADMIN_ROLES)
async def add_points(ctx, points: int, to_user: discord.Member, password: str):
    user = ctx.author
    embedvar = discord.Embed(title="Error 07",description=f"**{user.name}** has not registered yet. (ERR 07)\nPlease tell **{user.name}** to run command ``/setup``, then try again.",color=discord.Color.red(),)
    time = datetime.datetime.now(datetime.timezone.utc)
    time_format = datetime.datetime.strftime(time, "Today at %I:%M %p UTC.")
     
    if password == load_json("save_wpco.json", user.name, "user_data"):
        edit_json("save_wpco.json", f"{to_user.name}_pts", int(load_json("save_wpco.json", f"{to_user.name}_pts", "points"))+points, "points")

    try:
        embedvar = discord.Embed(
		title=f"Amount of added points for {to_user.name}:",
		description=f"**{to_user.name}**'s total points: {load_json('save_wpco.json', f'{to_user.name}_pts', 'points')}\nAdded by **{user.name}**",
		color=discord.Color.blue(),)
    except KeyError:
        print(f"ERR 07: {time_format} by {user.name}")
        
    embedvar.set_footer(text=time_format)
    embedvar.set_thumbnail(url="attachment://WPCO.png")
    await ctx.reply(file=logo, embed=embedvar)

@bot.hybrid_command(with_app_command = True, brief = "Get the number of points a user has/you have.")
@is_registered()
@is_blacklisted()
@commands.has_any_role(*ROLES)
async def points(ctx, user : discord.Member):
    embedvar = discord.Embed(title="Error 07",description=f"**{user.name}** has not registered yet. (ERR 07)\nPlease tell **{user.name}** to run command ``/setup``, then try again.",color=discord.Color.red(),)
    time = datetime.datetime.now(datetime.timezone.utc)
    time_format = time.strftime("Today at %I:%M %p UTC.")
    try:
        embedvar = discord.Embed(
		title=f"Amount of points for {user.name}:",
		description=f"Total points: {load_json('save_wpco.json', f'{user.name}_pts', 'points')}",
		color=discord.Color.blue(),)
    except KeyError:
        print(f"ERR 07: {time_format} by {user.name}")
    
    embedvar.set_footer(text=time_format)
    embedvar.set_thumbnail(url="attachment://WPCO.png")
    await ctx.reply(file=logo, embed=embedvar)

@bot.hybrid_command(with_app_command = True, brief = "Setup in order to run the bot. (RUN THIS COMMAND USING /setup.)")
@is_blacklisted()
@commands.has_any_role(*ROLES)
async def setup(ctx, password : str):
    user = ctx.author

    if len(password) < 8:
        await ctx.reply(":warning: You need a minimal of 8 characters for your password.")
    elif len(password) >= 8:
        try:
            load_json("save_wpco.json", f"{user.name}", "user_data")
            await ctx.reply(":warning: You have already done setup.")
        except KeyError:
            edit_json("save_wpco.json", f"{user.name}", password, "user_data")
            edit_json("save_wpco.json", f"{user.name}_pts", 0, "points")
            edit_json("save_wpco.json", f"{user.name}_rank", "EnO", "rank")
            safe_name = "".join(c for c in user.name if c.isalnum() or c in "-_")
            with open(f"./selfdep/{safe_name}.json", mode="w", encoding="utf-8") as outfile: json.dump({"id" : user.id, "deployments": {}, "deployment_unix": {}}, outfile)
            await ctx.reply(":white_check_mark: Setup complete. You may use the bot now.")

@bot.hybrid_command(with_app_command = True, brief = "Promotes a user to a specific rank (Note: check description, $help promote)", description = "PLEASE USE SHORT TERMS. e.g.(Cpt, GeN, SnO, etc.), ONLY WORKS FOR WPCO RANKS ONLY")
@is_registered()
@is_blacklisted()
@commands.has_any_role(*ADMIN_ROLES)
async def promote(ctx, member : discord.Member, rank : str, password : str):
    user = ctx.author
    time = datetime.datetime.now(datetime.timezone.utc)
    time_format = time.strftime("Today at %I:%M %p UTC.")

    try:
        load_json("save_wpco.json", f"{member.name}_rank", "rank")
        if password == load_json("save_wpco.json", user.name, "user_data") and load_json("save_wpco.json", f"{user.name}_rank", "rank") != rank:
            new_rank = RANKS[rank]
            edit_json("save_wpco.json", f"{member.name}_rank", rank, "rank")      
            await ctx.reply(f"{member.name}'s new rank: {new_rank}. Added by {user.name}")
    except KeyError:
        print(f"ERR 07: {time_format} by {user.name}")
        await ctx.reply(f"**{member.name}** has not registered yet. (ERR 07)\nPlease tell **{member.name}** to run command ``/setup``, then try again.")

@bot.hybrid_command(with_app_command = True, brief = "Promotes a user to a specific rank (Note: check description, $help promote)", description = "PLEASE USE SHORT TERMS. e.g.(Cpt, GeN, SnO, etc.), ONLY WORKS FOR WPCO RANKS ONLY")
@commands.has_any_role(*ROLES)
@is_registered()
@is_blacklisted()
async def check_password(ctx, password : str):
    #* thx plate
    user = ctx.author

    if password == load_json("save_wpco.json", user.name, "user_data"):
        await ctx.reply(":white_check_mark: Password is **correct**.")
    else:
        await ctx.reply(":x: Password is **incorrect**, try again.")

@bot.hybrid_command(with_app_command = True, brief = "Basic Help Command")
@commands.has_any_role(*ROLES)
@is_blacklisted()
async def help_s(ctx):
    await ctx.reply("""```Humor Commands:
  wack            ow my head hurts - ai bot??
  wake_yassin    
  say             Make the bot say anything....
  shucks
 
  Functional Commands:
  add_points      Add points to a member.
  check_password  Checks your current password
  help_s          Shows this message
  ping            Shows the bot's latency
  points          Get the number of points a user has/you have.
  promote         Promotes a user to a specific rank (Note: check description)      
  self_deploy     Used for logging Self-Deployments (Note: check description)
  setup           Setup in order to run the bot. (RUN THIS COMMAND USING /setup.)
  shutdown        Turns off the bot. (no need terminal killing)

Type /help_s command for more info on a command. (coming soon)
You can also type /help_s category for more info on a category. (coming soon)```""")

#* Events
@bot.event
async def on_ready():
    await bot.tree.sync()
    rprint(f'[[light_green]SUCCESSFUL[/light_green]] Synced slash commands for all servers.')
    rprint(f"[[light_green]VERSION[/light_green]] Discord.py version [bright_yellow]{discord.__version__}[/bright_yellow], Bot version [bright_yellow]{BOTVER}[/bright_yellow]")
    rprint(f'[[light_green]SUCCESSFUL[/light_green]] Logged in as [blue]{bot.user}[/blue] (ID: [#cccccc]{bot.user.id}[/#cccccc])')
    if not pymongo_installed:
        rprint(f'[[bright_red]ERROR[/bright_red]] pymongo not found, using alternative save_wpco.json and save_goc.json file.')
    find_save()
    #wait(1)
    #timer_input = int(input("Set automatic bot shutdown time in unix value (leave empty if manual shutdown): "))
    #await bot_timer(timer_input)
    rprint(f"[[bright_yellow]WARNING[/bright_yellow]] Please ping catamapp/yassin1234 for bot maintenance/unhandled errors.")
    if pymongo_installed:
        try:
            client = MongoClient(MONGO_URL)
            client.admin.command('ping')  # Test MongoDB connection
            rprint(f'[[light_green]SUCCESSFUL[/light_green]] MongoDB successfully connected.')
        except Exception:
            rprint(f'[[bright_red]ERROR[/bright_red]] MongoDB failed to connect.')
    rprint(f'[[light_green]COMPLETE[/light_green]] Bot has completed startup and now can be used.')
    try:
        await asyncio.to_thread(playsound.playsound, "sounds/beep.wav")
    except Exception as e:
        pass

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
        print(f"ERR 01: {time_format} by {user.name}")
        await ctx.send(file=logo, embed=make_error_embed(1))
    elif isinstance(error, commands.MissingRequiredArgument):
        #! no input
        print(f"ERR 02: {time_format} by {user.name}")
        await ctx.send(file=logo, embed=make_error_embed(2))
    elif isinstance(error, commands.BadArgument):
        #! input not valid/wrong
        print(f"ERR 03: {time_format} by {user.name}")
        await ctx.send(file=logo, embed=make_error_embed(3))
    elif isinstance(error, commands.MissingAnyRole):
        #! no perms?
        print(f"ERR 04: {time_format} by {user.name}")
        await ctx.send(file=logo, embed=make_error_embed(4))
    elif isinstance(error, discord.HTTPException):
        #! discord.py error
        print(f"ERR 05: {time_format} by {user.name}")
        await ctx.send(file=logo, embed=make_error_embed(5))
    elif isinstance(error, commands.CheckFailure):
        #! not registered
        print(f"ERR 06: {time_format} by {user.name}")
        await ctx.send(file=logo, embed=make_error_embed(6))
    elif isinstance(error, discord.Forbidden):
        #! bot doesnt have perm to do an action
        print(f"ERR 07: {time_format} by {user.name}")
        await ctx.send(file=logo, embed=make_error_embed(7))
    elif isinstance(error, commands.CommandRegistrationError):
        #! command registration failed
        print(f"ERR 08: {time_format} by {user.name}")
        await ctx.send(file=logo, embed=make_error_embed(8))
    elif isinstance(error, discord.PrivilegedIntentsRequired):
        #! intents not properly enabled
        print(f"ERR 09: {time_format} by {user.name}")
        await ctx.send(file=logo, embed=make_error_embed(9))
    elif isinstance(error, discord.ConnectionClosed):
        #! connection with discord closed
        print(f"ERR 10: {time_format} by {user.name}")
        await ctx.send(file=logo, embed=make_error_embed(10))
    elif isinstance(error, discord.GatewayNotFound):
        #! connection with discord gateaway failed
        print(f"ERR 11: {time_format} by {user.name}")
        await ctx.send(file=logo, embed=make_error_embed(11))
    else:
        #! what happen?? (python error or smth)
        rprint(f"[[bright_red]ERROR[/bright_red]] Unkown error: {error}\n{time_format}")
        await ctx.send(file=logo, embed=make_error_embed(error_msg=error))

bot.run(load_json("config.json", "token"))
