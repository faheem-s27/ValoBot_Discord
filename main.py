import json
import time
import aiohttp
import chromedriver_autoinstaller
import discord
import requests
import valorant
from discord.ext import commands
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from valclient import Client
from valorant_api import SyncValorantApi
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

chromedriver_autoinstaller.install()

TOKEN = 'Your Discord Token'

intents = discord.Intents().default()
intents.members = True

client = commands.Bot(command_prefix="-", intents=intents)
client.remove_command("help")

chromeOptions = Options()
chromeOptions.add_argument("--window-size=1920,1080")
chromeOptions.headless = True

KEY = "Your Riot API key"
#valoclient = valorant.Client(KEY)

valclient = Client(region="eu")
# valclient.activate()

BASEURL = "https://api.henrikdev.xyz/"


async def verify_name(ctx, riotname):
    if riotname is None:
        await ctx.send("--> Enter Riot Name:")
        riotname = await get_input_of_type(str, ctx)

    if riotname == "1":
        riotname = "SprinkledRainbow#1593"

    elif riotname == "2":
        riotname = "Slayzerzz#5427"

    elif riotname == "3":
        riotname = "素晴らしい Kyo#0419"

    substring = "#"
    if substring in riotname:
        RiotName = riotname.split('#')
    else:
        await ctx.send("--> Error, name must include #")
        return

    Name = RiotName[0]
    ID = RiotName[1]

    await ctx.send("--> Checking Name...")
    try:
        #valoclient.get_user_by_name(riotname)
        await ctx.send("--> Found User!")
    except Exception as e:
        await ctx.send("--> User doesnt exist!")
        return


def check(ctx):
    return lambda m: m.author == ctx.author and m.channel == ctx.channel


async def get_input_of_type(func, ctx):
    while True:
        try:
            msg = await client.wait_for('message', check=check(ctx))
            return func(msg.content)
        except ValueError:
            continue


@client.event
async def on_ready():
    # await client.change_presence(status=discord.Status.dnd, activity=discord.Activity(name="-help", type=2))
    await client.change_presence(
        activity=discord.Streaming(name="VALORANT", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab"))
    print(f'{client.user} has connected to Discord!')
    #await client.get_channel().send("I AM ALIVE!")


@client.command()
async def help(ctx):
    embed = discord.Embed()
    embed.set_author(name="ValoBot (Improved):")
    embed.set_thumbnail(url="https://img.icons8.com/plasticine/2x/valorant.png")
    embed.add_field(name="Commands:",
                    value=f"-valo\n-agent (name)\n-weapon (name)\n-live (Riot Name with #)\n-MMR (Riot Name with #)\n-announcements"
                          f"\n-dev_news\n-esports\n-updates\n-latest\n-h")
    embed.set_footer(text="Requested by " + ctx.author.name,
                     icon_url="https://img.icons8.com/plasticine/2x/valorant.png")
    await ctx.send(embed=embed)


@client.command()
async def h(ctx, riotname=None):
    if riotname is None:
        await ctx.send("Enter Username (I will make it save soon!)")
        riotname = await get_input_of_type(str, ctx)

    msg = await ctx.send("***Looking for name to see if it exists***")

    if riotname == "1":
        riotname = "SprinkledRainbow#1593"

    elif riotname == "2":
        riotname = "Slayzerzz#5427"

    elif riotname == "3":
        riotname = "素晴らしい Kyo#0419"

    elif riotname == "4":
        riotname = "AwesomeGamer#4100"

    substring = "#"
    if substring in riotname:
        RiotName = riotname.split('#')
    else:
        await ctx.send("Error, name must include #")
        return

    Name = RiotName[0]
    ID = RiotName[1]

    URL = f"https://api.henrikdev.xyz/valorant/v1/account/{Name}/{ID}"
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as r:
            data = json.loads(await r.text())

    if int(data["status"]) == 200:
        await ctx.send("YAY everything is working!", delete_after=1)
    else:
        print("Prepare for errors :)")
        await ctx.send("Currently there are server issues :(")
        return

    try:
        puuid = data["data"]["puuid"]
        UserName = data["data"]["name"]
        account_level = data["data"]["account_level"]
    except Exception as E:
        await ctx.send("Could not find name. User may not exist :(")
        return

    # PLAYERIMAGEURL = f"https://media.valorant-api.com/playercards/{playerCardID}/displayicon.png"

    await msg.edit(content=f"Found user **{UserName}**, Level: {account_level}")

    ENDPOINT = f"valorant/v1/by-puuid/mmr/eu/{puuid}"
    FINALURL = BASEURL + ENDPOINT

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(FINALURL) as r:
                RANKDATA = json.loads(await r.text())

            rank = RANKDATA["data"]["currenttierpatched"]
            ranknumber = RANKDATA["data"]["ranking_in_tier"]
            await msg.edit(
                content=f"Found user **{UserName}**, Level: {account_level}, In Rank: **{rank}**, **{ranknumber}**/100")
    except:
        await msg.edit(content=f"Found user **{UserName}**, Level: {account_level}, Unranked O_o")

    ENDPOINT = f"valorant/v3/by-puuid/matches/eu/{puuid}"
    FINALURL = BASEURL + ENDPOINT

    async with aiohttp.ClientSession() as session:
        async with session.get(FINALURL) as r:
            matchData = json.loads(await r.text())
            print(f"MATCHES FOR {UserName}: " + FINALURL)

    embed = discord.Embed(colour=discord.Colour.random())
    embed.set_author(name=f"{UserName} - Choose a match")

    foundAll = False
    num = 0
    while not foundAll:
        try:
            matchMap = matchData["data"][num]["metadata"]["map"]
            matchMode = matchData["data"][num]["metadata"]["mode"]
            matchdate = matchData["data"][num]["metadata"]["game_start_patched"]
            num = num + 1
            embed.add_field(name=f"Match #{num}", value=f"Map: **{matchMap}**"
                                                        f"\nMode: **{matchMode}**"
                                                        f"\nDate: **{matchdate}**", inline=True)
        except:
            foundAll = True

    for players in matchData["data"][0]["players"]["all_players"]:
        if players["name"] == UserName:
            PLAYERCARD = (players["player_card"])
            PLAYERIMAGEURL = f"https://media.valorant-api.com/playercards/{PLAYERCARD}/displayicon.png"
            embed.set_thumbnail(url=PLAYERIMAGEURL)

    await ctx.send(embed=embed)
    await ctx.send("Enter a number between 1 and 5")

    matchOption = await get_input_of_type(int, ctx)
    if matchOption < 0 or matchOption > 5:
        await ctx.send("Error :(")
        return
    matchOption = matchOption - 1
    matchID = matchData["data"][matchOption]["metadata"]["matchid"]
    matchMode = matchData["data"][matchOption]["metadata"]["mode"]
    matchMap = matchData["data"][matchOption]["metadata"]["map"]
    await ctx.send(f"Getting Information on Match #{matchOption + 1}! ({matchMode} on {matchMap})")

    MATCHURL = f"valorant/v2/match/{matchID}"
    FINALURL = BASEURL + MATCHURL
    print(matchID)

    async with aiohttp.ClientSession() as session:
        async with session.get(FINALURL) as r:
            matchData = json.loads(await r.text())
            print("MATCH DATA: " + FINALURL)

    if int(matchData["status"]) == 200:
        await ctx.send("Got the match. Extracting Information...")

    roundsPlayed = matchData["data"]["metadata"]["rounds_played"]
    redTeam = []
    blueTeam = []

    for name in matchData["data"]["players"]["red"]:
        redTeam.append(name["name"])
    for name in matchData["data"]["players"]["blue"]:
        blueTeam.append(name["name"])

    await ctx.send(
        "Red Team: " + str(redTeam) + "\n\nBlue Team: " + str(blueTeam) + "\n\nPlayed for " + str(roundsPlayed) + " rounds")

    await ctx.send("COMMAND DONE/MORE IS COMING SOON!")


@client.command()
async def updates(ctx):
    await ctx.send("Getting latest VALORANT updates...")

    URL = f"https://api.henrikdev.xyz/valorant/v1/website/en-us?filter=game_updates"
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as r:
            data = json.loads(await r.text())

    embed = discord.Embed(colour=discord.Colour.random())
    try:
        embed.set_author(name="VALORANT Game Update #1")
        embed.set_image(url=data["data"][0]["banner_url"])
        embed.add_field(name=str(data["data"][0]["title"]), value=str(data["data"][0]["url"]))
        await ctx.send(embed=embed)

        embed.set_author(name="VALORANT Game Update #2")
        embed.remove_field(0)
        embed.set_image(url=data["data"][1]["banner_url"])
        embed.add_field(name=str(data["data"][1]["title"]), value=str(data["data"][1]["url"]))
        await ctx.send(embed=embed)

        embed.set_author(name="VALORANT Game Update #3")
        embed.remove_field(0)
        embed.set_image(url=data["data"][2]["banner_url"])
        embed.add_field(name=str(data["data"][2]["title"]), value=str(data["data"][2]["url"]))
        await ctx.send(embed=embed)


    except Exception as e:
        await ctx.send("--> Error message: " + str(e))


@client.command()
async def latest(ctx):
    await ctx.send("Getting latest news of VALORANT...")

    URL = f"https://api.henrikdev.xyz/valorant/v1/website/en-us"
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as r:
            data = json.loads(await r.text())

    embed = discord.Embed(colour=discord.Colour.random())
    try:
        embed.set_author(name="VALORANT Update #1")
        embed.set_image(url=data["data"][0]["banner_url"])
        embed.add_field(name=str(data["data"][0]["title"]), value=str(data["data"][0]["url"]))
        await ctx.send(embed=embed)

        embed.set_author(name="VALORANT Update #2")
        embed.remove_field(0)
        embed.set_image(url=data["data"][1]["banner_url"])
        embed.add_field(name=str(data["data"][1]["title"]), value=str(data["data"][1]["url"]))
        await ctx.send(embed=embed)

        embed.set_author(name="VALORANT Update #3")
        embed.remove_field(0)
        embed.set_image(url=data["data"][2]["banner_url"])
        embed.add_field(name=str(data["data"][2]["title"]), value=str(data["data"][2]["url"]))
        await ctx.send(embed=embed)


    except Exception as e:
        await ctx.send("--> Error message: " + str(e))


@client.command()
async def announcements(ctx):
    await ctx.send("Getting latest VALORANT announcments...")

    URL = f"https://api.henrikdev.xyz/valorant/v1/website/en-us?filter=announcements"
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as r:
            data = json.loads(await r.text())

    embed = discord.Embed(colour=discord.Colour.random())
    try:
        embed.set_author(name="VALORANT Announcements #1")
        embed.set_image(url=data["data"][0]["banner_url"])
        embed.add_field(name=str(data["data"][0]["title"]), value=str(data["data"][0]["url"]))
        await ctx.send(embed=embed)

        embed.set_author(name="VALORANT Announcements #2")
        embed.remove_field(0)
        embed.set_image(url=data["data"][1]["banner_url"])
        embed.add_field(name=str(data["data"][1]["title"]), value=str(data["data"][1]["url"]))
        await ctx.send(embed=embed)

        embed.set_author(name="VALORANT Announcements #3")
        embed.remove_field(0)
        embed.set_image(url=data["data"][2]["banner_url"])
        embed.add_field(name=str(data["data"][2]["title"]), value=str(data["data"][2]["url"]))
        await ctx.send(embed=embed)


    except Exception as e:
        await ctx.send("--> Error message: " + str(e))


@client.command()
async def esports(ctx):
    await ctx.send("Getting latest E-sports news for VALORANT...")

    URL = "https://api.henrikdev.xyz/valorant/v1/website/en-us?filter=esports"
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as r:
            data = json.loads(await r.text())

    embed = discord.Embed(colour=discord.Colour.random())
    try:
        embed.set_author(name="VALORANT Esports #1")
        embed.set_image(url=data["data"][0]["banner_url"])
        embed.add_field(name=str(data["data"][0]["title"]), value=str(data["data"][0]["url"]))
        await ctx.send(embed=embed)

        embed.set_author(name="VALORANT Esports #2")
        embed.remove_field(0)
        embed.set_image(url=data["data"][1]["banner_url"])
        embed.add_field(name=str(data["data"][1]["title"]), value=str(data["data"][1]["url"]))
        await ctx.send(embed=embed)

        embed.set_author(name="VALORANT Esports #3")
        embed.remove_field(0)
        embed.set_image(url=data["data"][2]["banner_url"])
        embed.add_field(name=str(data["data"][2]["title"]), value=str(data["data"][2]["url"]))
        await ctx.send(embed=embed)


    except Exception as e:
        await ctx.send("--> Error message: " + str(e))


@client.command()
async def dev_news(ctx):
    await ctx.send("Getting Latest Dev news...")

    URL = f"https://api.henrikdev.xyz/valorant/v1/website/en-us?filter=dev"
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as r:
            data = json.loads(await r.text())

    embed = discord.Embed(colour=discord.Colour.random())
    try:
        embed.set_author(name="VALORANT Dev News #1")
        embed.set_image(url=data["data"][0]["banner_url"])
        embed.add_field(name=str(data["data"][0]["title"]), value=str(data["data"][0]["url"]))
        await ctx.send(embed=embed)

        embed.set_author(name="VALORANT Dev News #2")
        embed.remove_field(0)
        embed.set_image(url=data["data"][1]["banner_url"])
        embed.add_field(name=str(data["data"][1]["title"]), value=str(data["data"][1]["url"]))
        await ctx.send(embed=embed)

        embed.set_author(name="VALORANT Dev News #3")
        embed.remove_field(0)
        embed.set_image(url=data["data"][2]["banner_url"])
        embed.add_field(name=str(data["data"][2]["title"]), value=str(data["data"][2]["url"]))
        await ctx.send(embed=embed)


    except Exception as e:
        await ctx.send("--> Error message: " + str(e))


@client.command()
async def agent(ctx, agentName=None):
    if agentName is None:
        await ctx.send("--> Error, please say an agent name after command <--")
        return
    try:
        api = SyncValorantApi(language="en-US")
        agents = api.get_agents()
        agentData = agents.find_first(displayname=agentName)

        embed = discord.Embed()
        embed.set_author(name=f"Agent Name: {agentData.display_name}")
        embed.set_thumbnail(url=agentData.display_icon_small)
        embed.add_field(name=f"Role:", value=agentData.role.description)
        embed.add_field(name="Description", value=agentData.description)
        await ctx.send(embed=embed)

        abilites = discord.Embed()
        abilites.set_author(name=f"{agentData.display_name}'s Abilities")
        abilites.set_thumbnail(url=agentData.abilities[0].display_icon)
        abilites.add_field(name=f"First Ability: {str(agentData.abilities[0].display_name)}",
                           value=str(agentData.abilities[0].description))
        await ctx.send(embed=abilites)

        abilites = discord.Embed()
        abilites.set_author(name=f"{agentData.display_name}'s Abilities")
        abilites.set_thumbnail(url=agentData.abilities[1].display_icon)
        abilites.add_field(name=f"Second Ability: {str(agentData.abilities[1].display_name)}",
                           value=str(agentData.abilities[1].description))
        await ctx.send(embed=abilites)

        abilites = discord.Embed()
        abilites.set_author(name=f"{agentData.display_name}'s Abilities")
        abilites.set_thumbnail(url=agentData.abilities[2].display_icon)
        abilites.add_field(name=f"Third Ability: {str(agentData.abilities[2].display_name)}",
                           value=str(agentData.abilities[2].description))
        await ctx.send(embed=abilites)

        abilites = discord.Embed()
        abilites.set_author(name=f"{agentData.display_name}'s Ultimate")
        abilites.set_thumbnail(url=agentData.abilities[3].display_icon)
        abilites.add_field(name=f"Ultimate: {str(agentData.abilities[3].display_name)}",
                           value=str(agentData.abilities[3].description))
        await ctx.send(embed=abilites)

    except Exception as e:
        print(e)
        await ctx.send("--> Error, Agent Name WRONG <--")


@client.command()
async def weapon(ctx, weaponName=None):
    if weaponName is None:
        await ctx.send("--> Type a weapon name after the command! <--")
        return
    api = SyncValorantApi(language="en-US")
    weapons = api.get_weapons()
    try:
        weaponData = weapons.find_first(displayname=weaponName)

        embed = discord.Embed()
        embed.set_author(name=f"Weapon Name: {weaponData.display_name}")
        embed.set_thumbnail(url=weaponData.display_icon)
        embed.add_field(name=f"Stats!", value="Reload Time: " + str(weaponData.weapon_stats.reload_time_seconds)
                                              + "\nEquip Time " + str(weaponData.weapon_stats.equip_time_seconds))
        await ctx.send(embed=embed)

    except Exception as e:
        print(e)
        await ctx.send("--> ERROR, not a weapon name <--")


@client.command()
async def MMR(ctx, riotname=None, region=None):
    if riotname is None:
        await ctx.send("--> Enter Riot Name:")
        riotname = await get_input_of_type(str, ctx)

    if riotname == "1":
        riotname = "SprinkledRainbow#1593"

    elif riotname == "2":
        riotname = "Slayzerzz#5427"

    elif riotname == "3":
        riotname = "素晴らしい Kyo#0419"

    substring = "#"
    if substring in riotname:
        RiotName = riotname.split('#')
    else:
        await ctx.send("--> Error, name must include #")
        return

    Name = RiotName[0]
    ID = RiotName[1]

    await ctx.send("--> Checking Name...")
    try:
        #valoclient.get_user_by_name(riotname)
        await ctx.send("--> Found User!")
    except Exception as e:
        await ctx.send("--> User doesnt exist!")
        return

    if region is None:
        region = "EU"
        await ctx.send("Set Region to EU")
    region.lower()
    URL = f"https://api.henrikdev.xyz/valorant/v1/mmr-history/{region}/{Name}/{ID}"
    print(URL)
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as r:
            data = json.loads(await r.text())

    try:
        currentRank = data["data"][0]["currenttierpatched"]
        currentNumber = data["data"][0]["ranking_in_tier"]
        changetoMMR = int(data["data"][0]["mmr_change_to_last_game"])
        date = data["data"][0]["date"]
        elo = data["data"][0]["elo"]
        embed = discord.Embed(colour=discord.Colour.random())
        embed.set_author(name=f"{riotname}'s MMR")
        embed.add_field(name=f"Rank", value=currentRank)
        embed.add_field(name=f"Current MMR", value=str(currentNumber) + "/100")
        embed.add_field(name=f"Last MMR change", value=str(changetoMMR))
        embed.add_field(name=f"Current ELO", value=elo)
        await ctx.send(embed=embed)


    except Exception as e:
        print(e)
        await ctx.send("--> Error happened somewhere :0")


@client.command()
async def live(ctx, riotname=None):
    if riotname is None:
        await ctx.send("--> Enter Riot Name:")
        riotname = await get_input_of_type(str, ctx)

    if riotname == "1":
        riotname = "SprinkledRainbow#1593"

    elif riotname == "2":
        riotname = "Slayzerzz#5427"

    elif riotname == "3":
        riotname = "素晴らしい Kyo#0419"

    substring = "#"
    if substring in riotname:
        RiotName = riotname.split('#')
    else:
        await ctx.send("--> Error, name must include #")
        return

    Name = RiotName[0]
    ID = RiotName[1]

    msg = await ctx.send("--> Checking Name...")
    try:
        #valoclient.get_user_by_name(riotname)
        await msg.edit(content="--> Found User!")
    except Exception as e:
        await msg.edit(content="--> User doesnt exist!")
        return

    URL = f"https://api.henrikdev.xyz/valorant/v1/live-match/{Name}/{ID}"
    print(URL)

    msg = await ctx.send("Updating every 5 seconds")
    state = await ctx.send(f"Current state of **{Name}** = ")
    ingame = await ctx.send("In Game?: Checking")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(URL) as r:
                data = json.loads(await r.text())
        var = data["message"]
        await ctx.send("--> Error message: " + var)
    except:
        x = 0
        while x != 500:
            async with aiohttp.ClientSession() as session:
                async with session.get(URL) as r:
                    data = json.loads(await r.text())

            currentstate = data["data"]["current_state"]
            currentVersion = data["data"]["client_version"]
            await state.edit(content=f"Current state of **{Name}** = {currentstate}")
            if currentstate == "MENUS":
                menuGameMode = data["data"]["current_selected_gamemode"]
                await ctx.send(f"Current GameMode selected in Menu: {menuGameMode}")
            if currentstate == "INGAME":
                map = data["data"]["map"]
                gameMode = data["data"]["gamemode"]
                scoreAlly = data["data"]["score_ally_team"]
                scoreEnemy = data["data"]["score_enemy_team"]
                await ingame.edit(content=f"On {map} playing {gameMode}, Score is {scoreAlly}:{scoreEnemy}")
                x = x + 1
            if currentstate == "PREGAME":
                map = data["data"]["map"]
                gameMode = data["data"]["gamemode"]
                await ctx.send(f"Going to play {gameMode} on {map}")
                x = x + 1
            time.sleep(5)


@client.command()
async def valo(ctx, riotname=None, option=None, second_option=None):
    msg = await ctx.send("STILL IN DEVELOPMENT. Loading")
    driver = webdriver.Chrome(options=chromeOptions)

    startEmbed = discord.Embed()
    startEmbed.set_author(name=f"Enter Riot Name (including #):")

    if riotname is None:
        await msg.edit(embed=startEmbed)
        riotname = await get_input_of_type(str, ctx)

    if riotname == "1":
        riotname = "SprinkledRainbow#1593"

    elif riotname == "2":
        riotname = "Slayzerzz#5427"

    elif riotname == "3":
        riotname = "素晴らしい Kyo#0419"

    substring = "#"
    if substring in riotname:
        RiotName = riotname.split('#')
    else:
        await ctx.send("Error, name must include #")
        driver.close()
        return

    Name = RiotName[0]
    ID = RiotName[1]

    startEmbed.add_field(name=f"Riot Name:", value=f"--> **{Name}** with ID **{ID}** <--")
    startEmbed.set_thumbnail(url="https://img.icons8.com/plasticine/2x/valorant.png")
    await msg.edit(embed=startEmbed)

    startEmbed.add_field(name=f"Status:", value=f"--> Firstly verifying user exists... <--")
    await msg.edit(embed=startEmbed)
    try:
        #valoclient.get_user_by_name(riotname)
        startEmbed.remove_field(1)
        startEmbed.add_field(name=f"Status:", value=f"--> Found User! Accessing data. WAIT <--")
        await msg.edit(embed=startEmbed)
    except Exception as e:
        await ctx.send("--> User does not exist! <--")
        return
    VerifyNameURL = f"https://tracker.gg/valorant/profile/riot/{Name}%23{ID}/overview"
    driver.get(VerifyNameURL)
    time.sleep(3)
    try:
        var = driver.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.ph > div.ph__container > div.ph-details > div.ph-details__identifier > span > span.trn-ign__username').text
        startEmbed.remove_field(1)
        startEmbed.add_field(name=f"Status:", value=f"--> Found account **{var}**! :D <--")
        await msg.edit(embed=startEmbed)
    except:
        try:
            driver.get(VerifyNameURL)
            driver.find_element_by_class_name('lead')
            startEmbed.remove_field(1)
            startEmbed.add_field(name=f"Status:",
                                 value=f"--> It seems like this account is private so I cannot check info on it :/ <--")
            startEmbed.add_field(name="What to do:",
                                 value=f"If **{riotname}** is your account. You can sign in here!\n{VerifyNameURL}")

            await msg.edit(embed=startEmbed)
            return
        except NoSuchElementException:
            startEmbed.add_field(name=f"Status:",
                                 value=f"--> Username {riotname} does not exist! <--")
            await msg.edit(embed=startEmbed)
            return

    time.sleep(3)
    PlayerImage = driver.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.ph > div.ph__container > div.ph-avatar > svg > image').get_attribute(
        "href")
    embed = discord.Embed()
    embed.set_author(name=f"Enter number for Info on {riotname}")
    embed.set_thumbnail(url=PlayerImage)
    embed.add_field(name="Game mode Options:", value="1. Competitive"
                                                     "\n2. Unrated"
                                                     "\n3. Spikerush"
                                                     "\n4. Deathmatch")
    embed.add_field(name="Other Info:", value="5. Agents"
                                              "\n6. Weapons"
                                              "\n7. Maps"
                                              "\n8. Matches (Nearly done!)"
                                              "\n9. Total Time")
    embed.set_footer(text="VALORANT Main Menu")

    img_data = requests.get(PlayerImage).content
    with open('PlayerImage.png', 'wb') as handler:
        handler.write(img_data)

    img = Image.open("player-card-empty.png")
    playerimg = Image.open("PlayerImage.png")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 36)
    draw.text((180, 65), f"{var}#{ID}", (255, 255, 255), font=font)
    img.paste(playerimg, (41, 23))
    img.save("player-card.png")
    await ctx.send(file=discord.File("player-card.png"))

    if option is None:
        await msg.edit(embed=embed)
        await ctx.send("Select an option: ")
        option = await get_input_of_type(int, ctx)

    option = int(option)

    if option == 1:
        await competitive(ctx=ctx, riotName=Name, riotID=ID, d=driver)

    elif option == 2:
        await unrated(ctx=ctx, riotName=Name, riotID=ID, d=driver)

    elif option == 3:
        await spikerush(ctx=ctx, riotName=Name, riotID=ID, d=driver)

    elif option == 4:
        await deahmatch(ctx=ctx, riotName=Name, riotID=ID, d=driver)

    elif option == 5:
        embed = discord.Embed()
        embed.set_author(name=f"Enter number for Agent Info on {riotname}")
        embed.set_thumbnail(url="https://img.icons8.com/plasticine/2x/valorant.png")
        embed.add_field(name="Game mode Options:", value="1. Competitive"
                                                         "\n2. Unrated"
                                                         "\n3. Spikerush")
        embed.set_footer(text="VALORANT Agents")
        if second_option is None:
            await ctx.send(embed=embed)
            await ctx.send("Select an option:")
            second_option = await get_input_of_type(int, ctx)
        second_option = int(second_option)

        if second_option == 1:
            await agent_comp(ctx=ctx, riotName=Name, riotID=ID, d=driver)
        elif second_option == 2:
            await agent_unrated(ctx=ctx, riotName=Name, riotID=ID, d=driver)
        elif second_option == 3:
            await agent_spikerush(ctx=ctx, riotName=Name, riotID=ID, d=driver)
        else:
            await ctx.send("ERROR (probably not coded yet)")

    elif option == 6:
        embed = discord.Embed()
        embed.set_author(name=f"Enter number for Weapons Info on {riotname}")
        embed.set_thumbnail(url="https://img.icons8.com/plasticine/2x/valorant.png")
        embed.add_field(name="Game mode Options:", value="1. Competitive"
                                                         "\n2. Unrated"
                                                         "\n3. Spikerush")
        embed.set_footer(text="VALORANT Weapons")
        if second_option is None:
            await ctx.send(embed=embed)
            await ctx.send("Select an option:")
            second_option = await get_input_of_type(int, ctx)
        second_option = int(second_option)
        if second_option == 1:
            await weapons_comp(ctx=ctx, riotName=Name, riotID=ID, d=driver)
        elif second_option == 2:
            await weapons_unrated(ctx=ctx, riotName=Name, riotID=ID, d=driver)
        elif second_option == 3:
            await weapons_spikerushd(ctx=ctx, riotName=Name, riotID=ID, d=driver)
        else:
            await ctx.send("ERROR (probably not coded yet)")

    elif option == 7:
        embed = discord.Embed()
        embed.set_author(name=f"Enter number for Maps Info on {riotname}")
        embed.set_thumbnail(url="https://img.icons8.com/plasticine/2x/valorant.png")
        embed.add_field(name="Game mode Options:", value="1. Competitive"
                                                         "\n2. Unrated"
                                                         "\n3. Spikerush")
        embed.set_footer(text="VALORANT Maps")
        if second_option is None:
            await ctx.send(embed=embed)
            await ctx.send("Select an option:")
            second_option = await get_input_of_type(int, ctx)
        second_option = int(second_option)

        if second_option == 1:
            await maps_comp(ctx=ctx, riotName=Name, riotID=ID, d=driver)
        elif second_option == 2:
            await maps_unrated(ctx=ctx, riotName=Name, riotID=ID, d=driver)
        elif second_option == 3:
            await maps_spikerush(ctx=ctx, riotName=Name, riotID=ID, d=driver)
        else:
            await ctx.send("ERROR (probably not coded yet)")

    elif option == 8:
        embed = discord.Embed()
        embed.set_author(name=f"Enter number for Matches Info on {riotname}")
        embed.set_thumbnail(url="https://img.icons8.com/plasticine/2x/valorant.png")
        embed.add_field(name="Game mode Options:", value="1. Competitive"
                                                         "\n2. Unrated"
                                                         "\n3. Spikerush")
        embed.set_footer(text="VALORANT Matches")
        if second_option is None:
            await ctx.send(embed=embed)
            await ctx.send("Select an option:")
            second_option = await get_input_of_type(int, ctx)
        second_option = int(second_option)

        if second_option == 1:
            await matches_comp(ctx=ctx, riotName=Name, riotID=ID)
        if second_option == 2:
            await matches_unrated(ctx=ctx, riotName=Name, riotID=ID)
        else:
            await ctx.send("ERROR (probably not coded yet)")

    elif option == 9:
        await total_time(ctx=ctx, riotName=Name, riotID=ID, d=driver)

    else:
        await ctx.send("ERROR (probably not coded yet)")

    driver.close()
    await ctx.send("Finished", delete_after=1)


async def competitive(ctx, riotName: str, riotID: str, d: webdriver.Chrome):
    await ctx.send(f"--> Getting Comp stats for {riotName}#{riotID}")
    status = await ctx.send("--> Getting... <--")
    CompURL = f"https://tracker.gg/valorant/profile/riot/{riotName}%23{riotID}/overview?playlist=competitive"
    d.get(CompURL)
    time.sleep(3)
    rank = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.area-sidebar > div.rating.area-rating > div > div:nth-child(2) > div > div.rating-entry__info > div.value').text
    await status.edit(content="--> Got Rank! <--")
    rankImage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.area-sidebar > div.rating.area-rating > div > div:nth-child(2) > div > div.rating-entry__icon > img').get_attribute(
        "src")
    playTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.title > div > div > span.playtime').text
    await status.edit(content="--> Got Playtime! <--")
    matches = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.title > div > div > span.matches').text
    await status.edit(content="--> Got Matches Played! <--")
    mostkills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(10) > div > div.numbers > span.value').text
    winrate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    kd = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    killperround = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(7) > div > div.numbers > span.value').text
    wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(1) > div > div.numbers > span.value').text
    losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.highlighted.highlighted--giants > div.highlighted__content > div > div.valorant-winloss > svg > g:nth-child(3) > text:nth-child(2)').text
    kills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(2) > div > div.numbers > span.value').text
    deaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(4) > div > div.numbers > span.value').text
    assists = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(5) > div > div.numbers > span.value').text
    headshots = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(3) > div > div.numbers > span.value').text
    clutches = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(8) > div > div.numbers > span.value').text
    damage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    await status.edit(content="--> Got kills wins deaths! <--")
    time.sleep(1)
    await status.edit(content="--> Compiling information <--")

    embed = discord.Embed()
    embed.set_author(name=f"Competitive - {riotName}#{riotID}")
    embed.set_thumbnail(url=rankImage)
    embed.add_field(name="Rank Stats:", value=f"Rank: {rank}"
                                              f"\n{playTime}"
                                              f"\nPlayed **{matches}**")
    embed.add_field(name="Stats #1:", value=f"Wins: {wins}"
                                            f"\nLosses: {losses}"
                                            f"\nClutches: {clutches}"
                                            f"\nWinRate: {winrate}"
                                            f"\nDamage/round: {damage}"
                                            f"\nKills/round: {killperround}")
    embed.add_field(name="Stats #2", value=f"Most kills: {mostkills}"
                                           f"\nKills: {kills}"
                                           f"\nDeaths: {deaths}"
                                           f"\nK/D: {kd}"
                                           f"\nHeadshots: {headshots}"
                                           f"\nAssists: {assists}")
    embed.set_footer(text="VALORANT Competitive")
    await ctx.send(embed=embed)


async def unrated(ctx, riotName, riotID, d: webdriver.Chrome):
    await ctx.send(f"--> Getting Unrated stats for {riotName}#{riotID}")
    status = await ctx.send("--> Getting... <--")
    UnratedURL = f"https://tracker.gg/valorant/profile/riot/{riotName}%23{riotID}/overview?playlist=unrated"
    d.get(UnratedURL)
    time.sleep(3)
    playTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.title > div > div > span.playtime').text
    await status.edit(content="--> Got Playtime! <--")
    matches = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.title > div > div > span.matches').text
    await status.edit(content="--> Got Matches Played! <--")
    mostkills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(10) > div > div.numbers > span.value').text
    winrate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    kd = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    killperround = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(7) > div > div.numbers > span.value').text
    wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(1) > div > div.numbers > span.value').text
    losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.highlighted.highlighted--giants > div.highlighted__content > div > div.valorant-winloss > svg > g:nth-child(3) > text:nth-child(2)').text
    kills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(2) > div > div.numbers > span.value').text
    deaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(4) > div > div.numbers > span.value').text
    assists = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(5) > div > div.numbers > span.value').text
    headshots = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(3) > div > div.numbers > span.value').text
    clutches = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(8) > div > div.numbers > span.value').text
    damage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    await status.edit(content="--> Got kills wins deaths! <--")
    time.sleep(1)
    await status.edit(content="--> Compiling information <--")

    PlayerImage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.ph > div.ph__container > div.ph-avatar > svg > image').get_attribute(
        "href")

    embed = discord.Embed()
    embed.set_author(name=f"Unrated - {riotName}#{riotID}")
    embed.set_thumbnail(url=PlayerImage)
    embed.add_field(name="General:", value=f"{playTime}"
                                           f"\nPlayed **{matches}**")
    embed.add_field(name="Stats #1:", value=f"Wins: {wins}"
                                            f"\nLosses: {losses}"
                                            f"\nClutches: {clutches}"
                                            f"\nWinRate: {winrate}"
                                            f"\nDamage/round: {damage}"
                                            f"\nKills/round: {killperround}")
    embed.add_field(name="Stats #2", value=f"Most kills: {mostkills}"
                                           f"\nKills: {kills}"
                                           f"\nDeaths: {deaths}"
                                           f"\nK/D: {kd}"
                                           f"\nHeadshots: {headshots}"
                                           f"\nAssists: {assists}")
    embed.set_footer(text="VALORANT Unrated")
    await ctx.send(embed=embed)


async def spikerush(ctx, riotName, riotID, d: webdriver.Chrome):
    await ctx.send(f"--> Getting SpikeRush stats for {riotName}#{riotID}")
    status = await ctx.send("--> Getting... <--")
    SpikeRushURL = f"https://tracker.gg/valorant/profile/riot/{riotName}%23{riotID}/overview?playlist=spikerush"
    d.get(SpikeRushURL)
    time.sleep(3)
    playTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.title > div > div > span.playtime').text
    await status.edit(content="--> Got Playtime! <--")
    matches = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.title > div > div > span.matches').text
    await status.edit(content="--> Got Matches Played! <--")
    mostkills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(10) > div > div.numbers > span.value').text
    winrate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    kd = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    killperround = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(7) > div > div.numbers > span.value').text
    wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(1) > div > div.numbers > span.value').text
    losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.highlighted.highlighted--giants > div.highlighted__content > div > div.valorant-winloss > svg > g:nth-child(3) > text:nth-child(2)').text
    kills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(2) > div > div.numbers > span.value').text
    deaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(4) > div > div.numbers > span.value').text
    assists = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(5) > div > div.numbers > span.value').text
    headshots = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(3) > div > div.numbers > span.value').text
    clutches = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(8) > div > div.numbers > span.value').text
    damage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    await status.edit(content="--> Got kills wins deaths! <--")
    time.sleep(1)
    await status.edit(content="--> Compiling information <--")

    PlayerImage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.ph > div.ph__container > div.ph-avatar > svg > image').get_attribute(
        "href")

    embed = discord.Embed()
    embed.set_author(name=f"SpikeRush - {riotName}#{riotID}")
    embed.set_thumbnail(url=PlayerImage)
    embed.add_field(name="General:", value=f"{playTime}"
                                           f"\nPlayed **{matches}**")
    embed.add_field(name="Stats #1:", value=f"Wins: {wins}"
                                            f"\nLosses: {losses}"
                                            f"\nClutches: {clutches}"
                                            f"\nWinRate: {winrate}"
                                            f"\nDamage/round: {damage}"
                                            f"\nKills/round: {killperround}")
    embed.add_field(name="Stats #2", value=f"Most kills: {mostkills}"
                                           f"\nKills: {kills}"
                                           f"\nDeaths: {deaths}"
                                           f"\nK/D: {kd}"
                                           f"\nHeadshots: {headshots}"
                                           f"\nAssists: {assists}")
    embed.set_footer(text="VALORANT SpikeRush")
    await ctx.send(embed=embed)


async def deahmatch(ctx, riotName, riotID, d: webdriver.Chrome):
    await ctx.send(f"--> Getting Deathmatch stats for {riotName}#{riotID}")
    status = await ctx.send("--> Getting... <--")
    SpikeRushURL = f"https://tracker.gg/valorant/profile/riot/{riotName}%23{riotID}/overview?playlist=deathmatch"
    d.get(SpikeRushURL)
    time.sleep(3)
    playTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.title > div > div > span.playtime').text
    await status.edit(content="--> Got Playtime! <--")
    matches = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.title > div > div > span.matches').text
    await status.edit(content="--> Got Matches Played! <--")
    mostkills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(10) > div > div.numbers > span.value').text
    winrate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    kd = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    killperround = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(7) > div > div.numbers > span.value').text
    wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(1) > div > div.numbers > span.value').text
    losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.highlighted.highlighted--giants > div.highlighted__content > div > div.valorant-winloss > svg > g:nth-child(3) > text:nth-child(2)').text
    kills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(2) > div > div.numbers > span.value').text
    deaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(4) > div > div.numbers > span.value').text
    assists = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.main > div:nth-child(5) > div > div.numbers > span.value').text
    await status.edit(content="--> Got kills wins deaths! <--")
    time.sleep(1)
    await status.edit(content="--> Compiling information <--")

    PlayerImage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.ph > div.ph__container > div.ph-avatar > svg > image').get_attribute(
        "href")

    embed = discord.Embed()
    embed.set_author(name=f"Deathmatch - {riotName}#{riotID}")
    embed.set_thumbnail(url=PlayerImage)
    embed.add_field(name="General:", value=f"{playTime}"
                                           f"\nPlayed **{matches}**")
    embed.add_field(name="Stats #1:", value=f"Wins: {wins}"
                                            f"\nLosses: {losses}"
                                            f"\nWinRate: {winrate}"
                                            f"\nKills/round: {killperround}")
    embed.add_field(name="Stats #2", value=f"Most kills: {mostkills}"
                                           f"\nKills: {kills}"
                                           f"\nDeaths: {deaths}"
                                           f"\nK/D: {kd}"
                                           f"\nAssists: {assists}")
    embed.set_footer(text="VALORANT Deathmatch")
    await ctx.send(embed=embed)


async def total_time(ctx, riotName, riotID, d: webdriver.Chrome):
    await ctx.send(f"--> Getting time stats for {riotName}#{riotID}")
    status = await ctx.send("--> Getting... <--")
    CompURL = f"https://tracker.gg/valorant/profile/riot/{riotName}%23{riotID}/overview?playlist=competitive"
    d.get(CompURL)
    time.sleep(3)
    playTimeCOMP = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.title > div > div > span.playtime').text
    await status.edit(content="--> Got Comp time! <--")
    UnratedURL = f"https://tracker.gg/valorant/profile/riot/{riotName}%23{riotID}/overview?playlist=unrated"
    d.get(UnratedURL)
    time.sleep(3)
    playTimeUNRATED = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.title > div > div > span.playtime').text
    PlayerImage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.ph > div.ph__container > div.ph-avatar > svg > image').get_attribute(
        "href")
    await status.edit(content="--> Got Unrated time! <--")
    SRURL = f"https://tracker.gg/valorant/profile/riot/{riotName}%23{riotID}/overview?playlist=spikerush"
    d.get(SRURL)
    time.sleep(3)
    playTimeSPIKE = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.title > div > div > span.playtime').text
    await status.edit(content="--> Got Spikerush time! <--")
    DeathURL = f"https://tracker.gg/valorant/profile/riot/{riotName}%23{riotID}/overview?playlist=deathmatch"
    d.get(DeathURL)
    time.sleep(3)
    playTimeDEATH = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.container > div.segment-stats.area-main-stats.card.bordered.header-bordered.responsive > div.title > div > div > span.playtime').text
    await status.edit(content="--> Got Deathmatch time! <--")
    time.sleep(1)
    await status.edit(content="--> Compiling... <--", delete_after=3)

    embed = discord.Embed()
    embed.set_author(name=f"Total Time - {riotName}#{riotID}")
    embed.set_thumbnail(url=PlayerImage)
    embed.add_field(name="Competitive", value=f"{playTimeCOMP}")
    embed.add_field(name="Unrated", value=f"{playTimeUNRATED}")
    embed.add_field(name="Spikerush", value=f"{playTimeSPIKE}")
    embed.add_field(name="Deathmatch", value=f"{playTimeDEATH}")
    embed.set_footer(text="VALORANT Time")
    await ctx.send(embed=embed)


async def agent_comp(ctx, riotName, riotID, d: webdriver.Chrome):
    await ctx.send(f"--> Getting Agent stats for {riotName}#{riotID} (Comp) <--")
    msg = await ctx.send("--> Getting... <--")
    URL = f"https://tracker.gg/valorant/profile/riot/{riotName}%23{riotID}/agents?playlist=competitive"
    print(URL)
    d.get(URL)
    time.sleep(3)

    topAgentImage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div.agent__agent > div.agent__icon > img').get_attribute(
        "src")
    topagentName = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div.agent__agent > div.agent__name > span.agent__name-name').text
    topagentPlaytime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div.agent__agent > div.agent__name > span.agent__name-time').text
    topagentWinrate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div:nth-child(2)').text
    topagentKDratio = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div:nth-child(3)').text
    topagentKDA = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div:nth-child(4)').text
    topagentDamage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div:nth-child(5)').text

    topagentEmbed = discord.Embed()
    topagentEmbed.set_thumbnail(url=topAgentImage)
    topagentEmbed.set_author(name=f"Top Agent for {riotName}#{riotID} - Comp")
    topagentEmbed.add_field(name="Agent Name:", value=topagentName)
    topagentEmbed.add_field(name="Stats", value=f"{topagentPlaytime}"
                                                f"\nWinrate: {topagentWinrate}"
                                                f"\nKDA: {topagentKDA}"
                                                f"\nK/D: {topagentKDratio}"
                                                f"\nDamage/round: {topagentDamage}")

    await msg.edit(content="--> Top agent info collected! <--")

    topAgentImage2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div.agent__agent > div.agent__icon > img').get_attribute(
        "src")
    topagentName2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div.agent__agent > div.agent__name > span.agent__name-name').text
    topagentPlaytime2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div.agent__agent > div.agent__name > span.agent__name-time').text
    topagentWinrate2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div:nth-child(2)').text
    topagentKDratio2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div:nth-child(3)').text
    topagentKDA2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div:nth-child(4)').text
    topagentDamage2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div:nth-child(5)').text

    topagentEmbed2 = discord.Embed()
    topagentEmbed2.set_thumbnail(url=topAgentImage2)
    topagentEmbed2.set_author(name=f"2nd Top Agent for {riotName}#{riotID} - Comp")
    topagentEmbed2.add_field(name="Agent Name:", value=topagentName2)
    topagentEmbed2.add_field(name="Stats", value=f"{topagentPlaytime2}"
                                                 f"\nWinrate: {topagentWinrate2}"
                                                 f"\nKDA: {topagentKDA2}"
                                                 f"\nK/D: {topagentKDratio2}"
                                                 f"\nDamage/round: {topagentDamage2}")

    await msg.edit(content="--> 2nd Top agent info collected! <--")
    try:
        topAgentImage3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div.agent__agent > div.agent__icon > img').get_attribute(
            "src")
        topagentName3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div.agent__agent > div.agent__name > span.agent__name-name').text
        topagentPlaytime3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div.agent__agent > div.agent__name > span.agent__name-time').text
        topagentWinrate3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div:nth-child(2)').text
        topagentKDratio3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div:nth-child(3)').text
        topagentKDA3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div:nth-child(4)').text
        topagentDamage3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div:nth-child(5)').text

        topagentEmbed3 = discord.Embed()
        topagentEmbed3.set_thumbnail(url=topAgentImage3)
        topagentEmbed3.set_author(name=f"3rd Top Agent for {riotName}#{riotID} - Comp")
        topagentEmbed3.add_field(name="Agent Name:", value=topagentName3)
        topagentEmbed3.add_field(name="Stats", value=f"{topagentPlaytime3}"
                                                     f"\nWinrate: {topagentWinrate3}"
                                                     f"\nKDA: {topagentKDA3}"
                                                     f"\nK/D: {topagentKDratio3}"
                                                     f"\nDamage/round: {topagentDamage3}")

        await msg.edit(content="--> 3rd Top agent info collected! <--")
        time.sleep(1)
        await msg.edit(content="--> Sending 3 Top Agents <--")
        await ctx.send(embed=topagentEmbed)
        await ctx.send(embed=topagentEmbed2)
        await ctx.send(embed=topagentEmbed3)
    except NoSuchElementException:
        await msg.edit(content="--> Interesting... Only 2 agents played <--")
        time.sleep(2)
        await msg.edit(content="--> Sending 2 Top Agents <--")
        await ctx.send(embed=topagentEmbed)
        await ctx.send(embed=topagentEmbed2)


async def agent_unrated(ctx, riotName, riotID, d: webdriver.Chrome):
    await ctx.send(f"--> Getting Agent stats for {riotName}#{riotID} (Unrated) <--")
    msg = await ctx.send("--> Getting... <--")
    URL = f"https://tracker.gg/valorant/profile/riot/{riotName}%23{riotID}/agents?playlist=unrated"
    d.get(URL)
    time.sleep(3)

    topAgentImage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div.agent__agent > div.agent__icon > img').get_attribute(
        "src")
    topagentName = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div.agent__agent > div.agent__name > span.agent__name-name').text
    topagentPlaytime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div.agent__agent > div.agent__name > span.agent__name-time').text
    topagentWinrate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div:nth-child(2)').text
    topagentKDratio = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div:nth-child(3)').text
    topagentKDA = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div:nth-child(4)').text
    topagentDamage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div:nth-child(5)').text

    topagentEmbed = discord.Embed()
    topagentEmbed.set_thumbnail(url=topAgentImage)
    topagentEmbed.set_author(name=f"Top Agent for {riotName}#{riotID} - Unrated")
    topagentEmbed.add_field(name="Agent Name:", value=topagentName)
    topagentEmbed.add_field(name="Stats", value=f"{topagentPlaytime}"
                                                f"\nWinrate: {topagentWinrate}"
                                                f"\nKDA: {topagentKDA}"
                                                f"\nK/D: {topagentKDratio}"
                                                f"\nDamage/round: {topagentDamage}")

    await msg.edit(content="--> Top agent info collected! <--")

    topAgentImage2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div.agent__agent > div.agent__icon > img').get_attribute(
        "src")
    topagentName2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div.agent__agent > div.agent__name > span.agent__name-name').text
    topagentPlaytime2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div.agent__agent > div.agent__name > span.agent__name-time').text
    topagentWinrate2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div:nth-child(2)').text
    topagentKDratio2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div:nth-child(3)').text
    topagentKDA2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div:nth-child(4)').text
    topagentDamage2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div:nth-child(5)').text

    topagentEmbed2 = discord.Embed()
    topagentEmbed2.set_thumbnail(url=topAgentImage2)
    topagentEmbed2.set_author(name=f"2nd Top Agent for {riotName}#{riotID} - Unrated")
    topagentEmbed2.add_field(name="Agent Name:", value=topagentName2)
    topagentEmbed2.add_field(name="Stats", value=f"{topagentPlaytime2}"
                                                 f"\nWinrate: {topagentWinrate2}"
                                                 f"\nKDA: {topagentKDA2}"
                                                 f"\nK/D: {topagentKDratio2}"
                                                 f"\nDamage/round: {topagentDamage2}")

    await msg.edit(content="--> 2nd Top agent info collected! <--")
    try:
        topAgentImage3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div.agent__agent > div.agent__icon > img').get_attribute(
            "src")
        topagentName3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div.agent__agent > div.agent__name > span.agent__name-name').text
        topagentPlaytime3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div.agent__agent > div.agent__name > span.agent__name-time').text
        topagentWinrate3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div:nth-child(2)').text
        topagentKDratio3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div:nth-child(3)').text
        topagentKDA3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div:nth-child(4)').text
        topagentDamage3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div:nth-child(5)').text

        topagentEmbed3 = discord.Embed()
        topagentEmbed3.set_thumbnail(url=topAgentImage3)
        topagentEmbed3.set_author(name=f"3rd Top Agent for {riotName}#{riotID} - Unrated")
        topagentEmbed3.add_field(name="Agent Name:", value=topagentName3)
        topagentEmbed3.add_field(name="Stats", value=f"{topagentPlaytime3}"
                                                     f"\nWinrate: {topagentWinrate3}"
                                                     f"\nKDA: {topagentKDA3}"
                                                     f"\nK/D: {topagentKDratio3}"
                                                     f"\nDamage/round: {topagentDamage3}")

        await msg.edit(content="--> 3rd Top agent info collected! <--")
        time.sleep(1)
        await msg.edit(content="--> Sending 3 Top Agents <--")
        await ctx.send(embed=topagentEmbed)
        await ctx.send(embed=topagentEmbed2)
        await ctx.send(embed=topagentEmbed3)
    except NoSuchElementException:
        await msg.edit(content="--> Interesting... Only 2 agents played <--")
        time.sleep(2)
        await msg.edit(content="--> Sending 2 Top Agents <--")
        await ctx.send(embed=topagentEmbed)
        await ctx.send(embed=topagentEmbed2)


async def agent_spikerush(ctx, riotName, riotID, d: webdriver.Chrome):
    await ctx.send(f"--> Getting Agent stats for {riotName}#{riotID} (Spikerush) <--")
    msg = await ctx.send("--> Getting... <--")
    URL = f"https://tracker.gg/valorant/profile/riot/{riotName}%23{riotID}/agents?playlist=spikerush"
    d.get(URL)
    time.sleep(3)

    topAgentImage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div.agent__agent > div.agent__icon > img').get_attribute(
        "src")
    topagentName = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div.agent__agent > div.agent__name > span.agent__name-name').text
    topagentPlaytime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div.agent__agent > div.agent__name > span.agent__name-time').text
    topagentWinrate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div:nth-child(2)').text
    topagentKDratio = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div:nth-child(3)').text
    topagentKDA = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div:nth-child(4)').text
    topagentDamage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(2) > div > div:nth-child(5)').text

    topagentEmbed = discord.Embed()
    topagentEmbed.set_thumbnail(url=topAgentImage)
    topagentEmbed.set_author(name=f"Top Agent for {riotName}#{riotID} - Spikerush")
    topagentEmbed.add_field(name="Agent Name:", value=topagentName)
    topagentEmbed.add_field(name="Stats", value=f"{topagentPlaytime}"
                                                f"\nWinrate: {topagentWinrate}"
                                                f"\nKDA: {topagentKDA}"
                                                f"\nK/D: {topagentKDratio}"
                                                f"\nDamage/round: {topagentDamage}")

    await msg.edit(content="--> Top agent info collected! <--")
    try:
        topAgentImage2 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div.agent__agent > div.agent__icon > img').get_attribute(
            "src")
        topagentName2 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div.agent__agent > div.agent__name > span.agent__name-name').text
        topagentPlaytime2 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div.agent__agent > div.agent__name > span.agent__name-time').text
        topagentWinrate2 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div:nth-child(2)').text
        topagentKDratio2 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div:nth-child(3)').text
        topagentKDA2 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div:nth-child(4)').text
        topagentDamage2 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(4) > div > div:nth-child(5)').text

        topagentEmbed2 = discord.Embed()
        topagentEmbed2.set_thumbnail(url=topAgentImage2)
        topagentEmbed2.set_author(name=f"2nd Top Agent for {riotName}#{riotID} - Spikerush")
        topagentEmbed2.add_field(name="Agent Name:", value=topagentName2)
        topagentEmbed2.add_field(name="Stats", value=f"{topagentPlaytime2}"
                                                     f"\nWinrate: {topagentWinrate2}"
                                                     f"\nKDA: {topagentKDA2}"
                                                     f"\nK/D: {topagentKDratio2}"
                                                     f"\nDamage/round: {topagentDamage2}")

        await msg.edit(content="--> 2nd Top agent info collected! <--")

    except NoSuchElementException:
        await msg.edit(content="--> Interesting... Only 1 agent played <--")
        time.sleep(2)
        await msg.edit(content="--> Sending Top Agent <--")
        await ctx.send(embed=topagentEmbed)
        return
    try:
        topAgentImage3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div.agent__agent > div.agent__icon > img').get_attribute(
            "src")
        topagentName3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div.agent__agent > div.agent__name > span.agent__name-name').text
        topagentPlaytime3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div.agent__agent > div.agent__name > span.agent__name-time').text
        topagentWinrate3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div:nth-child(2)').text
        topagentKDratio3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div:nth-child(3)').text
        topagentKDA3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div:nth-child(4)').text
        topagentDamage3 = d.find_element_by_css_selector(
            '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small > div > div > div:nth-child(6) > div > div:nth-child(5)').text

        topagentEmbed3 = discord.Embed()
        topagentEmbed3.set_thumbnail(url=topAgentImage3)
        topagentEmbed3.set_author(name=f"3rd Top Agent for {riotName}#{riotID} - Spikerush")
        topagentEmbed3.add_field(name="Agent Name:", value=topagentName3)
        topagentEmbed3.add_field(name="Stats", value=f"{topagentPlaytime3}"
                                                     f"\nWinrate: {topagentWinrate3}"
                                                     f"\nKDA: {topagentKDA3}"
                                                     f"\nK/D: {topagentKDratio3}"
                                                     f"\nDamage/round: {topagentDamage3}")

        await msg.edit(content="--> 3rd Top agent info collected! <--")
        time.sleep(1)
        await msg.edit(content="--> Sending 3 Top Agents <--")
        await ctx.send(embed=topagentEmbed)
        await ctx.send(embed=topagentEmbed2)
        await ctx.send(embed=topagentEmbed3)
    except NoSuchElementException:
        await msg.edit(content="--> Interesting... Only 2 agents played <--")
        time.sleep(2)
        await msg.edit(content="--> Sending 2 Top Agents <--")
        await ctx.send(embed=topagentEmbed)
        await ctx.send(embed=topagentEmbed2)


async def weapons_comp(ctx, riotName, riotID, d: webdriver.Chrome):
    await ctx.send(f"--> Getting Weapons stats for {riotName}#{riotID} (Comp) <--")
    msg = await ctx.send("--> Getting... <--")
    URL = f"https://tracker.gg/valorant/profile/riot/{riotName}%23{riotID}/weapons?playlist=competitive"
    d.get(URL)
    time.sleep(3)

    topweaponImage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td.trn-table__column--left > div > div.segment-used__entry-image > img').get_attribute(
        "src")
    topweaponName = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td.trn-table__column--left > div > div.segment-used__tp > span.segment-used__tp-name').text
    topweaponType = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td.trn-table__column--left > div > div.segment-used__tp > span.segment-used__tp-sub').text
    topweaponKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td.trn-table__column--active.trn-table__column--best > div > span').text
    topweaponDiedTo = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td:nth-child(3) > div > span').text
    topweaponHeadshots = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td:nth-child(4) > div > span').text
    topweaponHeadshotsRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td:nth-child(5) > div > span').text
    topweaponDamage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td:nth-child(6) > div > span').text

    topweaponEmbed = discord.Embed()
    topweaponEmbed.set_thumbnail(url=topweaponImage)
    topweaponEmbed.set_author(name=f"Top weapon for {riotName}#{riotID} - Comp")
    topweaponEmbed.add_field(name=f"Weapon:", value=f"{topweaponName} - {topweaponType}")
    topweaponEmbed.add_field(name=f"Stats:", value=f"Kills: {topweaponKills}"
                                                   f"\nHeadshots: {topweaponHeadshots}"
                                                   f"\nHeadshots Rate: {topweaponHeadshotsRate}%"
                                                   f"\nDied to: {topweaponDiedTo}"
                                                   f"\nDamage/round: {topweaponDamage}")

    await msg.edit(content=f"--> Got top weapon stats! <--")

    topweaponImage2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td.trn-table__column--left > div > div.segment-used__entry-image > img').get_attribute(
        "src")
    topweaponName2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td.trn-table__column--left > div > div.segment-used__tp > span.segment-used__tp-name').text
    topweaponType2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td.trn-table__column--left > div > div.segment-used__tp > span.segment-used__tp-sub').text
    topweaponKills2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td.trn-table__column--active > div > span').text
    topweaponDiedTo2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td:nth-child(3) > div > span').text
    topweaponHeadshots2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td:nth-child(4) > div > span').text
    topweaponHeadshotsRate2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td:nth-child(5) > div > span').text
    topweaponDamage2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td:nth-child(6) > div > span').text

    topweaponEmbed2 = discord.Embed()
    topweaponEmbed2.set_thumbnail(url=topweaponImage2)
    topweaponEmbed2.set_author(name=f"2nd Top weapon for {riotName}#{riotID} - Comp")
    topweaponEmbed2.add_field(name=f"Weapon:", value=f"{topweaponName2} - {topweaponType2}")
    topweaponEmbed2.add_field(name=f"Stats:", value=f"Kills: {topweaponKills2}"
                                                    f"\nHeadshots: {topweaponHeadshots2}"
                                                    f"\nHeadshots Rate: {topweaponHeadshotsRate2}%"
                                                    f"\nDied to: {topweaponDiedTo2}"
                                                    f"\nDamage/round: {topweaponDamage2}")

    await msg.edit(content=f"--> Got 2nd top weapon stats! <--")

    topweaponImage3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td.trn-table__column--left > div > div.segment-used__entry-image > img').get_attribute(
        "src")
    topweaponName3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td.trn-table__column--left > div > div.segment-used__tp > span.segment-used__tp-name').text
    topweaponType3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td.trn-table__column--left > div > div.segment-used__tp > span.segment-used__tp-sub').text
    topweaponKills3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td.trn-table__column--active > div > span').text
    topweaponDiedTo3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td:nth-child(3) > div > span').text
    topweaponHeadshots3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td:nth-child(4) > div > span').text
    topweaponHeadshotsRate3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td:nth-child(5) > div > span').text
    topweaponDamage3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td:nth-child(6) > div > span').text

    topweaponEmbed3 = discord.Embed()
    topweaponEmbed3.set_thumbnail(url=topweaponImage3)
    topweaponEmbed3.set_author(name=f"3rd Top weapon for {riotName}#{riotID} - Comp")
    topweaponEmbed3.add_field(name=f"Weapon:", value=f"{topweaponName3} - {topweaponType3}")
    topweaponEmbed3.add_field(name=f"Stats:", value=f"Kills: {topweaponKills3}"
                                                    f"\nHeadshots: {topweaponHeadshots3}"
                                                    f"\nHeadshots Rate: {topweaponHeadshotsRate3}%"
                                                    f"\nDied to: {topweaponDiedTo3}"
                                                    f"\nDamage/round: {topweaponDamage3}")

    await msg.edit(content=f"--> Got 3rd top weapon stats! <--")
    time.sleep(2)
    await msg.edit(conten=f"--> Sending 3 top weapons <--")
    await ctx.send(embed=topweaponEmbed)
    await ctx.send(embed=topweaponEmbed2)
    await ctx.send(embed=topweaponEmbed3)


async def weapons_unrated(ctx, riotName, riotID, d: webdriver.Chrome):
    await ctx.send(f"--> Getting Weapons stats for {riotName}#{riotID} (Unrated) <--")
    msg = await ctx.send("--> Getting... <--")
    URL = f"https://tracker.gg/valorant/profile/riot/{riotName}%23{riotID}/weapons?playlist=unrated"
    d.get(URL)
    time.sleep(3)

    topweaponImage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td.trn-table__column--left > div > div.segment-used__entry-image > img').get_attribute(
        "src")
    topweaponName = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td.trn-table__column--left > div > div.segment-used__tp > span.segment-used__tp-name').text
    topweaponType = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td.trn-table__column--left > div > div.segment-used__tp > span.segment-used__tp-sub').text
    topweaponKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td.trn-table__column--active.trn-table__column--best > div > span').text
    topweaponDiedTo = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td:nth-child(3) > div > span').text
    topweaponHeadshots = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td:nth-child(4) > div > span').text
    topweaponHeadshotsRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td:nth-child(5) > div > span').text
    topweaponDamage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td:nth-child(6) > div > span').text

    topweaponEmbed = discord.Embed()
    topweaponEmbed.set_thumbnail(url=topweaponImage)
    topweaponEmbed.set_author(name=f"Top weapon for {riotName}#{riotID} - Unrated")
    topweaponEmbed.add_field(name=f"Weapon:", value=f"{topweaponName} - {topweaponType}")
    topweaponEmbed.add_field(name=f"Stats:", value=f"Kills: {topweaponKills}"
                                                   f"\nHeadshots: {topweaponHeadshots}"
                                                   f"\nHeadshots Rate: {topweaponHeadshotsRate}%"
                                                   f"\nDied to: {topweaponDiedTo}"
                                                   f"\nDamage/round: {topweaponDamage}")

    await msg.edit(content=f"--> Got top weapon stats! <--")

    topweaponImage2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td.trn-table__column--left > div > div.segment-used__entry-image > img').get_attribute(
        "src")
    topweaponName2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td.trn-table__column--left > div > div.segment-used__tp > span.segment-used__tp-name').text
    topweaponType2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td.trn-table__column--left > div > div.segment-used__tp > span.segment-used__tp-sub').text
    topweaponKills2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td.trn-table__column--active > div > span').text
    topweaponDiedTo2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td:nth-child(3) > div > span').text
    topweaponHeadshots2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td:nth-child(4) > div > span').text
    topweaponHeadshotsRate2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td:nth-child(5) > div > span').text
    topweaponDamage2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td:nth-child(6) > div > span').text

    topweaponEmbed2 = discord.Embed()
    topweaponEmbed2.set_thumbnail(url=topweaponImage2)
    topweaponEmbed2.set_author(name=f"2nd Top weapon for {riotName}#{riotID} - Unrated")
    topweaponEmbed2.add_field(name=f"Weapon:", value=f"{topweaponName2} - {topweaponType2}")
    topweaponEmbed2.add_field(name=f"Stats:", value=f"Kills: {topweaponKills2}"
                                                    f"\nHeadshots: {topweaponHeadshots2}"
                                                    f"\nHeadshots Rate: {topweaponHeadshotsRate2}%"
                                                    f"\nDied to: {topweaponDiedTo2}"
                                                    f"\nDamage/round: {topweaponDamage2}")

    await msg.edit(content=f"--> Got 2nd top weapon stats! <--")

    topweaponImage3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td.trn-table__column--left > div > div.segment-used__entry-image > img').get_attribute(
        "src")
    topweaponName3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td.trn-table__column--left > div > div.segment-used__tp > span.segment-used__tp-name').text
    topweaponType3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td.trn-table__column--left > div > div.segment-used__tp > span.segment-used__tp-sub').text
    topweaponKills3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td.trn-table__column--active > div > span').text
    topweaponDiedTo3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td:nth-child(3) > div > span').text
    topweaponHeadshots3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td:nth-child(4) > div > span').text
    topweaponHeadshotsRate3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td:nth-child(5) > div > span').text
    topweaponDamage3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td:nth-child(6) > div > span').text

    topweaponEmbed3 = discord.Embed()
    topweaponEmbed3.set_thumbnail(url=topweaponImage3)
    topweaponEmbed3.set_author(name=f"3rd Top weapon for {riotName}#{riotID} - Unrated")
    topweaponEmbed3.add_field(name=f"Weapon:", value=f"{topweaponName3} - {topweaponType3}")
    topweaponEmbed3.add_field(name=f"Stats:", value=f"Kills: {topweaponKills3}"
                                                    f"\nHeadshots: {topweaponHeadshots3}"
                                                    f"\nHeadshots Rate: {topweaponHeadshotsRate3}%"
                                                    f"\nDied to: {topweaponDiedTo3}"
                                                    f"\nDamage/round: {topweaponDamage3}")

    await msg.edit(content=f"--> Got 3rd top weapon stats! <--")
    time.sleep(2)
    await msg.edit(conten=f"--> Sending 3 top weapons <--")
    await ctx.send(embed=topweaponEmbed)
    await ctx.send(embed=topweaponEmbed2)
    await ctx.send(embed=topweaponEmbed3)


async def weapons_spikerushd(ctx, riotName, riotID, d: webdriver.Chrome):
    await ctx.send(f"--> Getting Weapons stats for {riotName}#{riotID} (Spikerush) <--")
    msg = await ctx.send("--> Getting... <--")
    URL = f"https://tracker.gg/valorant/profile/riot/{riotName}%23{riotID}/weapons?playlist=spikerush"
    d.get(URL)
    time.sleep(3)

    topweaponImage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td.trn-table__column--left > div > div.segment-used__entry-image > img').get_attribute(
        "src")
    topweaponName = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td.trn-table__column--left > div > div.segment-used__tp > span.segment-used__tp-name').text
    topweaponType = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td.trn-table__column--left > div > div.segment-used__tp > span.segment-used__tp-sub').text
    topweaponKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td.trn-table__column--active.trn-table__column--best > div > span').text
    topweaponDiedTo = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td:nth-child(3) > div > span').text
    topweaponHeadshots = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td:nth-child(4) > div > span').text
    topweaponHeadshotsRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td:nth-child(5) > div > span').text
    topweaponDamage = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(1) > td:nth-child(6) > div > span').text

    topweaponEmbed = discord.Embed()
    topweaponEmbed.set_thumbnail(url=topweaponImage)
    topweaponEmbed.set_author(name=f"Top weapon for {riotName}#{riotID} - Spikerush")
    topweaponEmbed.add_field(name=f"Weapon:", value=f"{topweaponName} - {topweaponType}")
    topweaponEmbed.add_field(name=f"Stats:", value=f"Kills: {topweaponKills}"
                                                   f"\nHeadshots: {topweaponHeadshots}"
                                                   f"\nHeadshots Rate: {topweaponHeadshotsRate}%"
                                                   f"\nDied to: {topweaponDiedTo}"
                                                   f"\nDamage/round: {topweaponDamage}")

    await msg.edit(content=f"--> Got top weapon stats! <--")

    topweaponImage2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td.trn-table__column--left > div > div.segment-used__entry-image > img').get_attribute(
        "src")
    topweaponName2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td.trn-table__column--left > div > div.segment-used__tp > span.segment-used__tp-name').text
    topweaponType2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td.trn-table__column--left > div > div.segment-used__tp > span.segment-used__tp-sub').text
    topweaponKills2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td.trn-table__column--active > div > span').text
    topweaponDiedTo2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td:nth-child(3) > div > span').text
    topweaponHeadshots2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td:nth-child(4) > div > span').text
    topweaponHeadshotsRate2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td:nth-child(5) > div > span').text
    topweaponDamage2 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(2) > td:nth-child(6) > div > span').text

    topweaponEmbed2 = discord.Embed()
    topweaponEmbed2.set_thumbnail(url=topweaponImage2)
    topweaponEmbed2.set_author(name=f"2nd Top weapon for {riotName}#{riotID} - Spikerush")
    topweaponEmbed2.add_field(name=f"Weapon:", value=f"{topweaponName2} - {topweaponType2}")
    topweaponEmbed2.add_field(name=f"Stats:", value=f"Kills: {topweaponKills2}"
                                                    f"\nHeadshots: {topweaponHeadshots2}"
                                                    f"\nHeadshots Rate: {topweaponHeadshotsRate2}%"
                                                    f"\nDied to: {topweaponDiedTo2}"
                                                    f"\nDamage/round: {topweaponDamage2}")

    await msg.edit(content=f"--> Got 2nd top weapon stats! <--")

    topweaponImage3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td.trn-table__column--left > div > div.segment-used__entry-image > img').get_attribute(
        "src")
    topweaponName3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td.trn-table__column--left > div > div.segment-used__tp > span.segment-used__tp-name').text
    topweaponType3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td.trn-table__column--left > div > div.segment-used__tp > span.segment-used__tp-sub').text
    topweaponKills3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td.trn-table__column--active > div > span').text
    topweaponDiedTo3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td:nth-child(3) > div > span').text
    topweaponHeadshots3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td:nth-child(4) > div > span').text
    topweaponHeadshotsRate3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td:nth-child(5) > div > span').text
    topweaponDamage3 = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.weapons > div > div.segment-used__table.trn-table__container > table > tbody > tr:nth-child(3) > td:nth-child(6) > div > span').text

    topweaponEmbed3 = discord.Embed()
    topweaponEmbed3.set_thumbnail(url=topweaponImage3)
    topweaponEmbed3.set_author(name=f"3rd Top weapon for {riotName}#{riotID} - Spikerush")
    topweaponEmbed3.add_field(name=f"Weapon:", value=f"{topweaponName3} - {topweaponType3}")
    topweaponEmbed3.add_field(name=f"Stats:", value=f"Kills: {topweaponKills3}"
                                                    f"\nHeadshots: {topweaponHeadshots3}"
                                                    f"\nHeadshots Rate: {topweaponHeadshotsRate3}%"
                                                    f"\nDied to: {topweaponDiedTo3}"
                                                    f"\nDamage/round: {topweaponDamage3}")

    await msg.edit(content=f"--> Got 3rd top weapon stats! <--")
    time.sleep(2)
    await msg.edit(conten=f"--> Sending 3 top weapons <--")
    await ctx.send(embed=topweaponEmbed)
    await ctx.send(embed=topweaponEmbed2)
    await ctx.send(embed=topweaponEmbed3)


async def maps_comp(ctx, riotName, riotID, d: webdriver.Chrome):
    await ctx.send(f"--> Getting Maps stats for {riotName}#{riotID} (Comp) <--")
    msg = await ctx.send("--> Getting... <--")
    URL = f"https://tracker.gg/valorant/profile/riot/{riotName}%23{riotID}/maps?playlist=competitive"
    d.get(URL)
    time.sleep(3)

    map1Name = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__header > div.map-stats__header-metadata > h2').text
    map1PlayTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map1MatchesPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__header > div.map-stats__header-metadata > div').text
    map1Wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    map1Losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(3) > div > div.numbers > span.value').text
    map1WinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map1KillsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map1DeathsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map1AssistsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map1RoundPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map1RoundsWon = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map1RoundLoss = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map1AttackKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map1AttackDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map1AttackWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map1DefenseKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map1DefenseDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map1DefenseWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map1Image = "https://gamertweak.com/wp-content/uploads/2020/06/valorant-ascent-map.jpg"

    embedMap1 = discord.Embed()
    embedMap1.set_thumbnail(url=map1Image)
    embedMap1.set_author(name=f"{map1Name} stats for {riotName}#{riotID} - Comp")
    embedMap1.add_field(name=f"Time stats", value=f"**{map1MatchesPlayed}**\nPlayed for **{map1PlayTime}**")
    embedMap1.add_field(name=f"General", value=f"Wins: {map1Wins}"
                                               f"\nLosses: {map1Losses}"
                                               f"\nWinrate: {map1WinRate}"
                                               f"\nKills/match: {map1KillsPerMatch}"
                                               f"\nDeaths/match: {map1DeathsPerMatch}"
                                               f"\nAssists/match: {map1AssistsPerMatch}")
    embedMap1.add_field(name=f"Round stats", value=f"Rounds Played: {map1RoundPlayed}"
                                                   f"\nRounds Won: {map1RoundsWon}"
                                                   f"\nRounds Lost: {map1RoundLoss}")
    embedMap1.add_field(name=f"Attacking Stats", value=f"WinRate: {map1AttackWinRate}"
                                                       f"\nKills: {map1AttackKills}"
                                                       f"\nDeaths: {map1AttackDeaths}")
    embedMap1.add_field(name=f"Defense Stats", value=f"WinRate: {map1DefenseWinRate}"
                                                     f"\nKills: {map1DefenseKills}"
                                                     f"\nDeaths: {map1DefenseDeaths}")
    await msg.edit(content=f"--> Got {map1Name} stats! <--")

    map2Name = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__header > div.map-stats__header-metadata > h2').text
    map2PlayTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map2MatchesPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__header > div.map-stats__header-metadata > div').text
    map2Wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    map2Losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(3) > div > div.numbers > span.value').text
    map2WinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map2KillsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map2DeathsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map2AssistsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map2RoundPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map2RoundsWon = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map2RoundLoss = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map2AttackKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map2AttackDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map2AttackWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map2DefenseKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map2DefenseDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map2DefenseWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map2Image = "https://staticg.sportskeeda.com/editor/2021/04/5701e-16192550715805-800.jpg"

    embedMap2 = discord.Embed()
    embedMap2.set_thumbnail(url=map2Image)
    embedMap2.set_author(name=f"{map2Name} stats for {riotName}#{riotID} - Comp")
    embedMap2.add_field(name=f"Time stats", value=f"**{map2MatchesPlayed}**\nPlayed for **{map2PlayTime}**")
    embedMap2.add_field(name=f"General", value=f"Wins: {map2Wins}"
                                               f"\nLosses: {map2Losses}"
                                               f"\nWinrate: {map2WinRate}"
                                               f"\nKills/match: {map2KillsPerMatch}"
                                               f"\nDeaths/match: {map2DeathsPerMatch}"
                                               f"\nAssists/match: {map2AssistsPerMatch}")
    embedMap2.add_field(name=f"Round stats", value=f"Rounds Played: {map2RoundPlayed}"
                                                   f"\nRounds Won: {map2RoundsWon}"
                                                   f"\nRounds Lost: {map2RoundLoss}")
    embedMap2.add_field(name=f"Attacking Stats", value=f"WinRate: {map2AttackWinRate}"
                                                       f"\nKills: {map2AttackKills}"
                                                       f"\nDeaths: {map2AttackDeaths}")
    embedMap2.add_field(name=f"Defense Stats", value=f"WinRate: {map2DefenseWinRate}"
                                                     f"\nKills: {map2DefenseKills}"
                                                     f"\nDeaths: {map2DefenseDeaths}")

    await msg.edit(content=f"--> Got {map2Name} stats! <--")

    map3Name = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__header > div.map-stats__header-metadata > h2').text
    map3PlayTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map3MatchesPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__header > div.map-stats__header-metadata > div').text
    map3Wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    map3Losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(3) > div > div.numbers > span.value').text
    map3WinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map3KillsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map3DeathsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map3AssistsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map3RoundPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map3RoundsWon = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map3RoundLoss = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map3AttackKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map3AttackDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map3AttackWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map3DefenseKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map3DefenseDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map3DefenseWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map3Image = "https://staticg.sportskeeda.com/editor/2020/07/85ebb-15936944284859-800.jpg"

    embedMap3 = discord.Embed()
    embedMap3.set_thumbnail(url=map3Image)
    embedMap3.set_author(name=f"{map3Name} stats for {riotName}#{riotID} - Comp")
    embedMap3.add_field(name=f"Time stats", value=f"**{map3MatchesPlayed}**\nPlayed for **{map3PlayTime}**")
    embedMap3.add_field(name=f"General", value=f"Wins: {map3Wins}"
                                               f"\nLosses: {map3Losses}"
                                               f"\nWinrate: {map3WinRate}"
                                               f"\nKills/match: {map3KillsPerMatch}"
                                               f"\nDeaths/match: {map3DeathsPerMatch}"
                                               f"\nAssists/match: {map3AssistsPerMatch}")
    embedMap3.add_field(name=f"Round stats", value=f"Rounds Played: {map3RoundPlayed}"
                                                   f"\nRounds Won: {map3RoundsWon}"
                                                   f"\nRounds Lost: {map3RoundLoss}")
    embedMap3.add_field(name=f"Attacking Stats", value=f"WinRate: {map3AttackWinRate}"
                                                       f"\nKills: {map3AttackKills}"
                                                       f"\nDeaths: {map3AttackDeaths}")
    embedMap3.add_field(name=f"Defense Stats", value=f"WinRate: {map3DefenseWinRate}"
                                                     f"\nKills: {map3DefenseKills}"
                                                     f"\nDeaths: {map3DefenseDeaths}")

    await msg.edit(content=f"--> Got {map3Name} stats! <--")

    # Map 4

    map4Name = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__header > div.map-stats__header-metadata > h2').text
    map4PlayTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map4MatchesPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__header > div.map-stats__header-metadata > div').text
    map4Wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    map4Losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(3) > div > div.numbers > span.value').text
    map4WinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map4KillsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map4DeathsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map4AssistsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map4RoundPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map4RoundsWon = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map4RoundLoss = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map4AttackKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map4AttackDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map4AttackWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map4DefenseKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map4DefenseDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map4DefenseWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map4Image = "https://static.wikia.nocookie.net/valorant/images/d/d6/Loading_Screen_Split.png"

    embedMap4 = discord.Embed()
    embedMap4.set_thumbnail(url=map4Image)
    embedMap4.set_author(name=f"{map4Name} stats for {riotName}#{riotID} - Comp")
    embedMap4.add_field(name=f"Time stats", value=f"**{map4MatchesPlayed}**\nPlayed for **{map4PlayTime}**")
    embedMap4.add_field(name=f"General", value=f"Wins: {map4Wins}"
                                               f"\nLosses: {map4Losses}"
                                               f"\nWinrate: {map4WinRate}"
                                               f"\nKills/match: {map4KillsPerMatch}"
                                               f"\nDeaths/match: {map4DeathsPerMatch}"
                                               f"\nAssists/match: {map4AssistsPerMatch}")
    embedMap4.add_field(name=f"Round stats", value=f"Rounds Played: {map4RoundPlayed}"
                                                   f"\nRounds Won: {map4RoundsWon}"
                                                   f"\nRounds Lost: {map4RoundLoss}")
    embedMap4.add_field(name=f"Attacking Stats", value=f"WinRate: {map4AttackWinRate}"
                                                       f"\nKills: {map4AttackKills}"
                                                       f"\nDeaths: {map4AttackDeaths}")
    embedMap4.add_field(name=f"Defense Stats", value=f"WinRate: {map4DefenseWinRate}"
                                                     f"\nKills: {map4DefenseKills}"
                                                     f"\nDeaths: {map4DefenseDeaths}")

    await msg.edit(content=f"--> Got {map4Name} stats! <--")

    # Map 5

    map5Name = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__header > div.map-stats__header-metadata > h2').text
    map5PlayTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map5MatchesPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__header > div.map-stats__header-metadata > div').text
    map5Wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    map5Losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(3) > div > div.numbers > span.value').text
    map5WinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map5KillsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map5DeathsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map5AssistsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map5RoundPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map5RoundsWon = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map5RoundLoss = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map5AttackKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map5AttackDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map5AttackWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map5DefenseKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map5DefenseDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map5DefenseWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map5Image = "https://static.wikia.nocookie.net/valorant/images/3/34/Loading_Icebox.png"

    embedMap5 = discord.Embed()
    embedMap5.set_thumbnail(url=map5Image)
    embedMap5.set_author(name=f"{map5Name} stats for {riotName}#{riotID} - Comp")
    embedMap5.add_field(name=f"Time stats", value=f"**{map5MatchesPlayed}**\nPlayed for **{map5PlayTime}**")
    embedMap5.add_field(name=f"General", value=f"Wins: {map5Wins}"
                                               f"\nLosses: {map5Losses}"
                                               f"\nWinrate: {map5WinRate}"
                                               f"\nKills/match: {map5KillsPerMatch}"
                                               f"\nDeaths/match: {map5DeathsPerMatch}"
                                               f"\nAssists/match: {map5AssistsPerMatch}")
    embedMap5.add_field(name=f"Round stats", value=f"Rounds Played: {map5RoundPlayed}"
                                                   f"\nRounds Won: {map5RoundsWon}"
                                                   f"\nRounds Lost: {map5RoundLoss}")
    embedMap5.add_field(name=f"Attacking Stats", value=f"WinRate: {map5AttackWinRate}"
                                                       f"\nKills: {map5AttackKills}"
                                                       f"\nDeaths: {map5AttackDeaths}")
    embedMap5.add_field(name=f"Defense Stats", value=f"WinRate: {map5DefenseWinRate}"
                                                     f"\nKills: {map5DefenseKills}"
                                                     f"\nDeaths: {map5DefenseDeaths}")

    await msg.edit(content=f"--> Got {map5Name} stats! <--")

    # Map 6

    map6Name = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__header > div.map-stats__header-metadata > h2').text
    map6PlayTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map6MatchesPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__header > div.map-stats__header-metadata > div').text
    map6Wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    map6Losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(3) > div > div.numbers > span.value').text
    map6WinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map6KillsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map6DeathsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map6AssistsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map6RoundPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map6RoundsWon = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map6RoundLoss = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map6AttackKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map6AttackDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map6AttackWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map6DefenseKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map6DefenseDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map6DefenseWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map6Image = "https://static.wikia.nocookie.net/valorant/images/1/1e/Valorant_Loading_Breeze.png/"

    embedMap6 = discord.Embed()
    embedMap6.set_thumbnail(url=map6Image)
    embedMap6.set_author(name=f"{map6Name} stats for {riotName}#{riotID} - Comp")
    embedMap6.add_field(name=f"Time stats", value=f"**{map6MatchesPlayed}**\nPlayed for **{map6PlayTime}**")
    embedMap6.add_field(name=f"General", value=f"Wins: {map6Wins}"
                                               f"\nLosses: {map6Losses}"
                                               f"\nWinrate: {map6WinRate}"
                                               f"\nKills/match: {map6KillsPerMatch}"
                                               f"\nDeaths/match: {map6DeathsPerMatch}"
                                               f"\nAssists/match: {map6AssistsPerMatch}")
    embedMap6.add_field(name=f"Round stats", value=f"Rounds Played: {map6RoundPlayed}"
                                                   f"\nRounds Won: {map6RoundsWon}"
                                                   f"\nRounds Lost: {map6RoundLoss}")
    embedMap6.add_field(name=f"Attacking Stats", value=f"WinRate: {map6AttackWinRate}"
                                                       f"\nKills: {map6AttackKills}"
                                                       f"\nDeaths: {map6AttackDeaths}")
    embedMap6.add_field(name=f"Defense Stats", value=f"WinRate: {map6DefenseWinRate}"
                                                     f"\nKills: {map6DefenseKills}"
                                                     f"\nDeaths: {map6DefenseDeaths}")

    await msg.edit(content=f"--> Got {map6Name} stats! <--")

    # End
    await msg.edit(content=f"--> Compiling information... <--")
    await ctx.send(embed=embedMap1)
    await ctx.send(embed=embedMap2)
    await ctx.send(embed=embedMap3)
    await ctx.send(embed=embedMap4)
    await ctx.send(embed=embedMap5)
    await ctx.send(embed=embedMap6)


async def maps_unrated(ctx, riotName, riotID, d: webdriver.Chrome):
    await ctx.send(f"--> Getting Maps stats for {riotName}#{riotID} (Unrated) <--")
    msg = await ctx.send("--> Getting... <--")
    URL = f"https://tracker.gg/valorant/profile/riot/{riotName}%23{riotID}/maps?playlist=unrated"
    d.get(URL)
    time.sleep(3)

    map1Name = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__header > div.map-stats__header-metadata > h2').text
    map1PlayTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map1MatchesPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__header > div.map-stats__header-metadata > div').text
    map1Wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    map1Losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(3) > div > div.numbers > span.value').text
    map1WinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map1KillsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map1DeathsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map1AssistsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map1RoundPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map1RoundsWon = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map1RoundLoss = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map1AttackKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map1AttackDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map1AttackWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map1DefenseKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map1DefenseDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map1DefenseWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map1Image = "https://gamertweak.com/wp-content/uploads/2020/06/valorant-ascent-map.jpg"

    embedMap1 = discord.Embed()
    embedMap1.set_thumbnail(url=map1Image)
    embedMap1.set_author(name=f"{map1Name} stats for {riotName}#{riotID} - Unrated")
    embedMap1.add_field(name=f"Time stats", value=f"**{map1MatchesPlayed}**\nPlayed for **{map1PlayTime}**")
    embedMap1.add_field(name=f"General", value=f"Wins: {map1Wins}"
                                               f"\nLosses: {map1Losses}"
                                               f"\nWinrate: {map1WinRate}"
                                               f"\nKills/match: {map1KillsPerMatch}"
                                               f"\nDeaths/match: {map1DeathsPerMatch}"
                                               f"\nAssists/match: {map1AssistsPerMatch}")
    embedMap1.add_field(name=f"Round stats", value=f"Rounds Played: {map1RoundPlayed}"
                                                   f"\nRounds Won: {map1RoundsWon}"
                                                   f"\nRounds Lost: {map1RoundLoss}")
    embedMap1.add_field(name=f"Attacking Stats", value=f"WinRate: {map1AttackWinRate}"
                                                       f"\nKills: {map1AttackKills}"
                                                       f"\nDeaths: {map1AttackDeaths}")
    embedMap1.add_field(name=f"Defense Stats", value=f"WinRate: {map1DefenseWinRate}"
                                                     f"\nKills: {map1DefenseKills}"
                                                     f"\nDeaths: {map1DefenseDeaths}")
    await msg.edit(content=f"--> Got {map1Name} stats! <--")

    map2Name = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__header > div.map-stats__header-metadata > h2').text
    map2PlayTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map2MatchesPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__header > div.map-stats__header-metadata > div').text
    map2Wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    map2Losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(3) > div > div.numbers > span.value').text
    map2WinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map2KillsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map2DeathsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map2AssistsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map2RoundPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map2RoundsWon = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map2RoundLoss = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map2AttackKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map2AttackDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map2AttackWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map2DefenseKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map2DefenseDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map2DefenseWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map2Image = "https://staticg.sportskeeda.com/editor/2021/04/5701e-16192550715805-800.jpg"

    embedMap2 = discord.Embed()
    embedMap2.set_thumbnail(url=map2Image)
    embedMap2.set_author(name=f"{map2Name} stats for {riotName}#{riotID} - Unrated")
    embedMap2.add_field(name=f"Time stats", value=f"**{map2MatchesPlayed}**\nPlayed for **{map2PlayTime}**")
    embedMap2.add_field(name=f"General", value=f"Wins: {map2Wins}"
                                               f"\nLosses: {map2Losses}"
                                               f"\nWinrate: {map2WinRate}"
                                               f"\nKills/match: {map2KillsPerMatch}"
                                               f"\nDeaths/match: {map2DeathsPerMatch}"
                                               f"\nAssists/match: {map2AssistsPerMatch}")
    embedMap2.add_field(name=f"Round stats", value=f"Rounds Played: {map2RoundPlayed}"
                                                   f"\nRounds Won: {map2RoundsWon}"
                                                   f"\nRounds Lost: {map2RoundLoss}")
    embedMap2.add_field(name=f"Attacking Stats", value=f"WinRate: {map2AttackWinRate}"
                                                       f"\nKills: {map2AttackKills}"
                                                       f"\nDeaths: {map2AttackDeaths}")
    embedMap2.add_field(name=f"Defense Stats", value=f"WinRate: {map2DefenseWinRate}"
                                                     f"\nKills: {map2DefenseKills}"
                                                     f"\nDeaths: {map2DefenseDeaths}")

    await msg.edit(content=f"--> Got {map2Name} stats! <--")

    map3Name = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__header > div.map-stats__header-metadata > h2').text
    map3PlayTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map3MatchesPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__header > div.map-stats__header-metadata > div').text
    map3Wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    map3Losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(3) > div > div.numbers > span.value').text
    map3WinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map3KillsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map3DeathsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map3AssistsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map3RoundPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map3RoundsWon = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map3RoundLoss = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map3AttackKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map3AttackDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map3AttackWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map3DefenseKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map3DefenseDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map3DefenseWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map3Image = "https://staticg.sportskeeda.com/editor/2020/07/85ebb-15936944284859-800.jpg"

    embedMap3 = discord.Embed()
    embedMap3.set_thumbnail(url=map3Image)
    embedMap3.set_author(name=f"{map3Name} stats for {riotName}#{riotID} - Unrated")
    embedMap3.add_field(name=f"Time stats", value=f"**{map3MatchesPlayed}**\nPlayed for **{map3PlayTime}**")
    embedMap3.add_field(name=f"General", value=f"Wins: {map3Wins}"
                                               f"\nLosses: {map3Losses}"
                                               f"\nWinrate: {map3WinRate}"
                                               f"\nKills/match: {map3KillsPerMatch}"
                                               f"\nDeaths/match: {map3DeathsPerMatch}"
                                               f"\nAssists/match: {map3AssistsPerMatch}")
    embedMap3.add_field(name=f"Round stats", value=f"Rounds Played: {map3RoundPlayed}"
                                                   f"\nRounds Won: {map3RoundsWon}"
                                                   f"\nRounds Lost: {map3RoundLoss}")
    embedMap3.add_field(name=f"Attacking Stats", value=f"WinRate: {map3AttackWinRate}"
                                                       f"\nKills: {map3AttackKills}"
                                                       f"\nDeaths: {map3AttackDeaths}")
    embedMap3.add_field(name=f"Defense Stats", value=f"WinRate: {map3DefenseWinRate}"
                                                     f"\nKills: {map3DefenseKills}"
                                                     f"\nDeaths: {map3DefenseDeaths}")

    await msg.edit(content=f"--> Got {map3Name} stats! <--")

    # Map 4

    map4Name = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__header > div.map-stats__header-metadata > h2').text
    map4PlayTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map4MatchesPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__header > div.map-stats__header-metadata > div').text
    map4Wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    map4Losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(3) > div > div.numbers > span.value').text
    map4WinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map4KillsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map4DeathsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map4AssistsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map4RoundPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map4RoundsWon = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map4RoundLoss = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map4AttackKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map4AttackDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map4AttackWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map4DefenseKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map4DefenseDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map4DefenseWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map4Image = "https://static.wikia.nocookie.net/valorant/images/d/d6/Loading_Screen_Split.png"

    embedMap4 = discord.Embed()
    embedMap4.set_thumbnail(url=map4Image)
    embedMap4.set_author(name=f"{map4Name} stats for {riotName}#{riotID} - Unrated")
    embedMap4.add_field(name=f"Time stats", value=f"**{map4MatchesPlayed}**\nPlayed for **{map4PlayTime}**")
    embedMap4.add_field(name=f"General", value=f"Wins: {map4Wins}"
                                               f"\nLosses: {map4Losses}"
                                               f"\nWinrate: {map4WinRate}"
                                               f"\nKills/match: {map4KillsPerMatch}"
                                               f"\nDeaths/match: {map4DeathsPerMatch}"
                                               f"\nAssists/match: {map4AssistsPerMatch}")
    embedMap4.add_field(name=f"Round stats", value=f"Rounds Played: {map4RoundPlayed}"
                                                   f"\nRounds Won: {map4RoundsWon}"
                                                   f"\nRounds Lost: {map4RoundLoss}")
    embedMap4.add_field(name=f"Attacking Stats", value=f"WinRate: {map4AttackWinRate}"
                                                       f"\nKills: {map4AttackKills}"
                                                       f"\nDeaths: {map4AttackDeaths}")
    embedMap4.add_field(name=f"Defense Stats", value=f"WinRate: {map4DefenseWinRate}"
                                                     f"\nKills: {map4DefenseKills}"
                                                     f"\nDeaths: {map4DefenseDeaths}")

    await msg.edit(content=f"--> Got {map4Name} stats! <--")

    # Map 5

    map5Name = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__header > div.map-stats__header-metadata > h2').text
    map5PlayTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map5MatchesPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__header > div.map-stats__header-metadata > div').text
    map5Wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    map5Losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(3) > div > div.numbers > span.value').text
    map5WinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map5KillsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map5DeathsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map5AssistsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map5RoundPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map5RoundsWon = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map5RoundLoss = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map5AttackKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map5AttackDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map5AttackWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map5DefenseKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map5DefenseDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map5DefenseWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map5Image = "https://static.wikia.nocookie.net/valorant/images/3/34/Loading_Icebox.png"

    embedMap5 = discord.Embed()
    embedMap5.set_thumbnail(url=map5Image)
    embedMap5.set_author(name=f"{map5Name} stats for {riotName}#{riotID} - Unrated")
    embedMap5.add_field(name=f"Time stats", value=f"**{map5MatchesPlayed}**\nPlayed for **{map5PlayTime}**")
    embedMap5.add_field(name=f"General", value=f"Wins: {map5Wins}"
                                               f"\nLosses: {map5Losses}"
                                               f"\nWinrate: {map5WinRate}"
                                               f"\nKills/match: {map5KillsPerMatch}"
                                               f"\nDeaths/match: {map5DeathsPerMatch}"
                                               f"\nAssists/match: {map5AssistsPerMatch}")
    embedMap5.add_field(name=f"Round stats", value=f"Rounds Played: {map5RoundPlayed}"
                                                   f"\nRounds Won: {map5RoundsWon}"
                                                   f"\nRounds Lost: {map5RoundLoss}")
    embedMap5.add_field(name=f"Attacking Stats", value=f"WinRate: {map5AttackWinRate}"
                                                       f"\nKills: {map5AttackKills}"
                                                       f"\nDeaths: {map5AttackDeaths}")
    embedMap5.add_field(name=f"Defense Stats", value=f"WinRate: {map5DefenseWinRate}"
                                                     f"\nKills: {map5DefenseKills}"
                                                     f"\nDeaths: {map5DefenseDeaths}")

    await msg.edit(content=f"--> Got {map5Name} stats! <--")

    # Map 6

    map6Name = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__header > div.map-stats__header-metadata > h2').text
    map6PlayTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map6MatchesPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__header > div.map-stats__header-metadata > div').text
    map6Wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    map6Losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(3) > div > div.numbers > span.value').text
    map6WinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map6KillsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map6DeathsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map6AssistsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map6RoundPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map6RoundsWon = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map6RoundLoss = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map6AttackKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map6AttackDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map6AttackWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map6DefenseKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map6DefenseDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map6DefenseWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map6Image = "https://static.wikia.nocookie.net/valorant/images/1/1e/Valorant_Loading_Breeze.png/"

    embedMap6 = discord.Embed()
    embedMap6.set_thumbnail(url=map6Image)
    embedMap6.set_author(name=f"{map6Name} stats for {riotName}#{riotID} - Unrated")
    embedMap6.add_field(name=f"Time stats", value=f"**{map6MatchesPlayed}**\nPlayed for **{map6PlayTime}**")
    embedMap6.add_field(name=f"General", value=f"Wins: {map6Wins}"
                                               f"\nLosses: {map6Losses}"
                                               f"\nWinrate: {map6WinRate}"
                                               f"\nKills/match: {map6KillsPerMatch}"
                                               f"\nDeaths/match: {map6DeathsPerMatch}"
                                               f"\nAssists/match: {map6AssistsPerMatch}")
    embedMap6.add_field(name=f"Round stats", value=f"Rounds Played: {map6RoundPlayed}"
                                                   f"\nRounds Won: {map6RoundsWon}"
                                                   f"\nRounds Lost: {map6RoundLoss}")
    embedMap6.add_field(name=f"Attacking Stats", value=f"WinRate: {map6AttackWinRate}"
                                                       f"\nKills: {map6AttackKills}"
                                                       f"\nDeaths: {map6AttackDeaths}")
    embedMap6.add_field(name=f"Defense Stats", value=f"WinRate: {map6DefenseWinRate}"
                                                     f"\nKills: {map6DefenseKills}"
                                                     f"\nDeaths: {map6DefenseDeaths}")

    await msg.edit(content=f"--> Got {map6Name} stats! <--")

    # End
    await msg.edit(content=f"--> Compiling information... <--")
    await ctx.send(embed=embedMap1)
    await ctx.send(embed=embedMap2)
    await ctx.send(embed=embedMap3)
    await ctx.send(embed=embedMap4)
    await ctx.send(embed=embedMap5)
    await ctx.send(embed=embedMap6)


async def maps_spikerush(ctx, riotName, riotID, d: webdriver.Chrome):
    await ctx.send(f"--> Getting Maps stats for {riotName}#{riotID} (Spikerush) <--")
    msg = await ctx.send("--> Getting... <--")
    URL = f"https://tracker.gg/valorant/profile/riot/{riotName}%23{riotID}/maps?playlist=spikerush"
    d.get(URL)
    time.sleep(3)

    map1Name = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__header > div.map-stats__header-metadata > h2').text
    map1PlayTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map1MatchesPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__header > div.map-stats__header-metadata > div').text
    map1Wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    map1Losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(3) > div > div.numbers > span.value').text
    map1WinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map1KillsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map1DeathsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map1AssistsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map1RoundPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map1RoundsWon = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map1RoundLoss = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map1AttackKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map1AttackDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map1AttackWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map1DefenseKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map1DefenseDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map1DefenseWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(1) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map1Image = "https://gamertweak.com/wp-content/uploads/2020/06/valorant-ascent-map.jpg"

    embedMap1 = discord.Embed()
    embedMap1.set_thumbnail(url=map1Image)
    embedMap1.set_author(name=f"{map1Name} stats for {riotName}#{riotID} - Spikerush")
    embedMap1.add_field(name=f"Time stats", value=f"**{map1MatchesPlayed}**\nPlayed for **{map1PlayTime}**")
    embedMap1.add_field(name=f"General", value=f"Wins: {map1Wins}"
                                               f"\nLosses: {map1Losses}"
                                               f"\nWinrate: {map1WinRate}"
                                               f"\nKills/match: {map1KillsPerMatch}"
                                               f"\nDeaths/match: {map1DeathsPerMatch}"
                                               f"\nAssists/match: {map1AssistsPerMatch}")
    embedMap1.add_field(name=f"Round stats", value=f"Rounds Played: {map1RoundPlayed}"
                                                   f"\nRounds Won: {map1RoundsWon}"
                                                   f"\nRounds Lost: {map1RoundLoss}")
    embedMap1.add_field(name=f"Attacking Stats", value=f"WinRate: {map1AttackWinRate}"
                                                       f"\nKills: {map1AttackKills}"
                                                       f"\nDeaths: {map1AttackDeaths}")
    embedMap1.add_field(name=f"Defense Stats", value=f"WinRate: {map1DefenseWinRate}"
                                                     f"\nKills: {map1DefenseKills}"
                                                     f"\nDeaths: {map1DefenseDeaths}")
    await msg.edit(content=f"--> Got {map1Name} stats! <--")

    map2Name = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__header > div.map-stats__header-metadata > h2').text
    map2PlayTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map2MatchesPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__header > div.map-stats__header-metadata > div').text
    map2Wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    map2Losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(3) > div > div.numbers > span.value').text
    map2WinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map2KillsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map2DeathsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map2AssistsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map2RoundPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map2RoundsWon = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map2RoundLoss = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map2AttackKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map2AttackDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map2AttackWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map2DefenseKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map2DefenseDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map2DefenseWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(2) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map2Image = "https://staticg.sportskeeda.com/editor/2021/04/5701e-16192550715805-800.jpg"

    embedMap2 = discord.Embed()
    embedMap2.set_thumbnail(url=map2Image)
    embedMap2.set_author(name=f"{map2Name} stats for {riotName}#{riotID} - Spikerush")
    embedMap2.add_field(name=f"Time stats", value=f"**{map2MatchesPlayed}**\nPlayed for **{map2PlayTime}**")
    embedMap2.add_field(name=f"General", value=f"Wins: {map2Wins}"
                                               f"\nLosses: {map2Losses}"
                                               f"\nWinrate: {map2WinRate}"
                                               f"\nKills/match: {map2KillsPerMatch}"
                                               f"\nDeaths/match: {map2DeathsPerMatch}"
                                               f"\nAssists/match: {map2AssistsPerMatch}")
    embedMap2.add_field(name=f"Round stats", value=f"Rounds Played: {map2RoundPlayed}"
                                                   f"\nRounds Won: {map2RoundsWon}"
                                                   f"\nRounds Lost: {map2RoundLoss}")
    embedMap2.add_field(name=f"Attacking Stats", value=f"WinRate: {map2AttackWinRate}"
                                                       f"\nKills: {map2AttackKills}"
                                                       f"\nDeaths: {map2AttackDeaths}")
    embedMap2.add_field(name=f"Defense Stats", value=f"WinRate: {map2DefenseWinRate}"
                                                     f"\nKills: {map2DefenseKills}"
                                                     f"\nDeaths: {map2DefenseDeaths}")

    await msg.edit(content=f"--> Got {map2Name} stats! <--")

    map3Name = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__header > div.map-stats__header-metadata > h2').text
    map3PlayTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map3MatchesPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__header > div.map-stats__header-metadata > div').text
    map3Wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    map3Losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(3) > div > div.numbers > span.value').text
    map3WinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map3KillsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map3DeathsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map3AssistsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map3RoundPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map3RoundsWon = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map3RoundLoss = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map3AttackKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map3AttackDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map3AttackWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map3DefenseKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map3DefenseDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map3DefenseWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(3) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map3Image = "https://staticg.sportskeeda.com/editor/2020/07/85ebb-15936944284859-800.jpg"

    embedMap3 = discord.Embed()
    embedMap3.set_thumbnail(url=map3Image)
    embedMap3.set_author(name=f"{map3Name} stats for {riotName}#{riotID} - Spikerush")
    embedMap3.add_field(name=f"Time stats", value=f"**{map3MatchesPlayed}**\nPlayed for **{map3PlayTime}**")
    embedMap3.add_field(name=f"General", value=f"Wins: {map3Wins}"
                                               f"\nLosses: {map3Losses}"
                                               f"\nWinrate: {map3WinRate}"
                                               f"\nKills/match: {map3KillsPerMatch}"
                                               f"\nDeaths/match: {map3DeathsPerMatch}"
                                               f"\nAssists/match: {map3AssistsPerMatch}")
    embedMap3.add_field(name=f"Round stats", value=f"Rounds Played: {map3RoundPlayed}"
                                                   f"\nRounds Won: {map3RoundsWon}"
                                                   f"\nRounds Lost: {map3RoundLoss}")
    embedMap3.add_field(name=f"Attacking Stats", value=f"WinRate: {map3AttackWinRate}"
                                                       f"\nKills: {map3AttackKills}"
                                                       f"\nDeaths: {map3AttackDeaths}")
    embedMap3.add_field(name=f"Defense Stats", value=f"WinRate: {map3DefenseWinRate}"
                                                     f"\nKills: {map3DefenseKills}"
                                                     f"\nDeaths: {map3DefenseDeaths}")

    await msg.edit(content=f"--> Got {map3Name} stats! <--")

    # Map 4

    map4Name = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__header > div.map-stats__header-metadata > h2').text
    map4PlayTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map4MatchesPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__header > div.map-stats__header-metadata > div').text
    map4Wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    map4Losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(3) > div > div.numbers > span.value').text
    map4WinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map4KillsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map4DeathsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map4AssistsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map4RoundPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map4RoundsWon = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map4RoundLoss = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map4AttackKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map4AttackDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map4AttackWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map4DefenseKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map4DefenseDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map4DefenseWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(4) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map4Image = "https://static.wikia.nocookie.net/valorant/images/d/d6/Loading_Screen_Split.png"

    embedMap4 = discord.Embed()
    embedMap4.set_thumbnail(url=map4Image)
    embedMap4.set_author(name=f"{map4Name} stats for {riotName}#{riotID} - Spikerush")
    embedMap4.add_field(name=f"Time stats", value=f"**{map4MatchesPlayed}**\nPlayed for **{map4PlayTime}**")
    embedMap4.add_field(name=f"General", value=f"Wins: {map4Wins}"
                                               f"\nLosses: {map4Losses}"
                                               f"\nWinrate: {map4WinRate}"
                                               f"\nKills/match: {map4KillsPerMatch}"
                                               f"\nDeaths/match: {map4DeathsPerMatch}"
                                               f"\nAssists/match: {map4AssistsPerMatch}")
    embedMap4.add_field(name=f"Round stats", value=f"Rounds Played: {map4RoundPlayed}"
                                                   f"\nRounds Won: {map4RoundsWon}"
                                                   f"\nRounds Lost: {map4RoundLoss}")
    embedMap4.add_field(name=f"Attacking Stats", value=f"WinRate: {map4AttackWinRate}"
                                                       f"\nKills: {map4AttackKills}"
                                                       f"\nDeaths: {map4AttackDeaths}")
    embedMap4.add_field(name=f"Defense Stats", value=f"WinRate: {map4DefenseWinRate}"
                                                     f"\nKills: {map4DefenseKills}"
                                                     f"\nDeaths: {map4DefenseDeaths}")

    await msg.edit(content=f"--> Got {map4Name} stats! <--")

    # Map 5

    map5Name = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__header > div.map-stats__header-metadata > h2').text
    map5PlayTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map5MatchesPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__header > div.map-stats__header-metadata > div').text
    map5Wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    map5Losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(3) > div > div.numbers > span.value').text
    map5WinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map5KillsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map5DeathsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map5AssistsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map5RoundPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map5RoundsWon = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map5RoundLoss = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map5AttackKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map5AttackDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map5AttackWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map5DefenseKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map5DefenseDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map5DefenseWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(5) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map5Image = "https://static.wikia.nocookie.net/valorant/images/3/34/Loading_Icebox.png"

    embedMap5 = discord.Embed()
    embedMap5.set_thumbnail(url=map5Image)
    embedMap5.set_author(name=f"{map5Name} stats for {riotName}#{riotID} - Spikerush")
    embedMap5.add_field(name=f"Time stats", value=f"**{map5MatchesPlayed}**\nPlayed for **{map5PlayTime}**")
    embedMap5.add_field(name=f"General", value=f"Wins: {map5Wins}"
                                               f"\nLosses: {map5Losses}"
                                               f"\nWinrate: {map5WinRate}"
                                               f"\nKills/match: {map5KillsPerMatch}"
                                               f"\nDeaths/match: {map5DeathsPerMatch}"
                                               f"\nAssists/match: {map5AssistsPerMatch}")
    embedMap5.add_field(name=f"Round stats", value=f"Rounds Played: {map5RoundPlayed}"
                                                   f"\nRounds Won: {map5RoundsWon}"
                                                   f"\nRounds Lost: {map5RoundLoss}")
    embedMap5.add_field(name=f"Attacking Stats", value=f"WinRate: {map5AttackWinRate}"
                                                       f"\nKills: {map5AttackKills}"
                                                       f"\nDeaths: {map5AttackDeaths}")
    embedMap5.add_field(name=f"Defense Stats", value=f"WinRate: {map5DefenseWinRate}"
                                                     f"\nKills: {map5DefenseKills}"
                                                     f"\nDeaths: {map5DefenseDeaths}")

    await msg.edit(content=f"--> Got {map5Name} stats! <--")

    # Map 6

    map6Name = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__header > div.map-stats__header-metadata > h2').text
    map6PlayTime = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map6MatchesPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__header > div.map-stats__header-metadata > div').text
    map6Wins = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(2) > div > div.numbers > span.value').text
    map6Losses = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(3) > div > div.numbers > span.value').text
    map6WinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(1) > div > div.numbers > span.value').text
    map6KillsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map6DeathsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map6AssistsPerMatch = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__giant-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map6RoundPlayed = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(4) > div > div.numbers > span.value').text
    map6RoundsWon = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(5) > div > div.numbers > span.value').text
    map6RoundLoss = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__other-stats > div:nth-child(6) > div > div.numbers > span.value').text
    map6AttackKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map6AttackDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map6AttackWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(1) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map6DefenseKills = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(2) > div > div.stat-value__graph-value').text
    map6DefenseDeaths = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(4) > div > div.stat-value__graph-value').text
    map6DefenseWinRate = d.find_element_by_css_selector(
        '#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid.trn-grid--small.maps > div:nth-child(6) > div.map-stats__content > div > div.map-stats__objective-stats > div:nth-child(2) > div.objective-stats-graph__stats > div:nth-child(8)').text
    map6Image = "https://static.wikia.nocookie.net/valorant/images/1/1e/Valorant_Loading_Breeze.png/"

    embedMap6 = discord.Embed()
    embedMap6.set_thumbnail(url=map6Image)
    embedMap6.set_author(name=f"{map6Name} stats for {riotName}#{riotID} - Spikerush")
    embedMap6.add_field(name=f"Time stats", value=f"**{map6MatchesPlayed}**\nPlayed for **{map6PlayTime}**")
    embedMap6.add_field(name=f"General", value=f"Wins: {map6Wins}"
                                               f"\nLosses: {map6Losses}"
                                               f"\nWinrate: {map6WinRate}"
                                               f"\nKills/match: {map6KillsPerMatch}"
                                               f"\nDeaths/match: {map6DeathsPerMatch}"
                                               f"\nAssists/match: {map6AssistsPerMatch}")
    embedMap6.add_field(name=f"Round stats", value=f"Rounds Played: {map6RoundPlayed}"
                                                   f"\nRounds Won: {map6RoundsWon}"
                                                   f"\nRounds Lost: {map6RoundLoss}")
    embedMap6.add_field(name=f"Attacking Stats", value=f"WinRate: {map6AttackWinRate}"
                                                       f"\nKills: {map6AttackKills}"
                                                       f"\nDeaths: {map6AttackDeaths}")
    embedMap6.add_field(name=f"Defense Stats", value=f"WinRate: {map6DefenseWinRate}"
                                                     f"\nKills: {map6DefenseKills}"
                                                     f"\nDeaths: {map6DefenseDeaths}")

    await msg.edit(content=f"--> Got {map6Name} stats! <--")

    # End
    await msg.edit(content=f"--> Compiling information... <--")
    await ctx.send(embed=embedMap1)
    await ctx.send(embed=embedMap2)
    await ctx.send(embed=embedMap3)
    await ctx.send(embed=embedMap4)
    await ctx.send(embed=embedMap5)
    await ctx.send(embed=embedMap6)


async def matches_comp(ctx, riotName, riotID):
    msg = await ctx.send("--> Getting Match stats <--")
    history_api = f"https://api.henrikdev.xyz/valorant/v1/account/{riotName}/{riotID}"
    async with aiohttp.ClientSession() as session:
        async with session.get(history_api) as r:
            data = json.loads(await r.text())

    fullName = riotName + "#" + riotID

    puuid = data["data"]["puuid"]
    await msg.edit(content=f"--> Player ID: {puuid}")
    history = valclient.fetch_match_history(puuid=puuid, queue_id="competitive")
    matchID = history["History"][0]["MatchID"]
    await msg.edit(content=f"--> Last Competitive Match ID: {matchID}")
    GAMEINFO = await match_stats(match_id=matchID)
    await msg.edit(content=f"--> Successfully got last match details! <--")

    map_name = GAMEINFO[0]["match_info"]["map_name"]
    map_URL = GAMEINFO[0]["match_info"]["map_image_url"]
    RedPoints = GAMEINFO[0]["Red"]["rounds_won"]
    BluePoints = GAMEINFO[0]["Blue"]["rounds_won"]
    date = GAMEINFO[0]["match_info"]["start"]
    substring = "T"
    if substring in date:
        date = date.split('T')

    dateDay = date[0]
    dateTime = date[1]

    substring = "."
    if substring in dateTime:
        dateTime = dateTime.split('.')

    duration = float(GAMEINFO[0]["match_info"]["duration"])
    duration = duration / 60000
    duration = "{:.2f}".format(duration)
    players = GAMEINFO[1]
    blueTeam = []
    redTeam = []

    for players in players:
        if GAMEINFO[1][players]["team"] == "Blue":
            blueTeam.append(players)
        else:
            redTeam.append(players)

    redPlayer1 = redTeam[0]
    redPlayer2 = redTeam[1]
    redPlayer3 = redTeam[2]
    redPlayer4 = redTeam[3]
    redPlayer5 = redTeam[4]

    bluePlayer1 = blueTeam[0]
    bluePlayer2 = blueTeam[1]
    bluePlayer3 = blueTeam[2]
    bluePlayer4 = blueTeam[3]
    bluePlayer5 = blueTeam[4]

    embed = discord.Embed()
    embed.set_thumbnail(url=map_URL)
    embed.set_author(name=f"Match details for {riotName} (Comp)")
    embed.add_field(name=f"Map", value=map_name)
    embed.add_field(name=f"Duration", value=f"{duration} minutes")
    embed.add_field(name=f"Date", value=f"On {dateDay} at {dateTime[0]}")
    embed.add_field(name="Points", value=f"Red : Blue\n{RedPoints} : {BluePoints}")
    embed.add_field(name=f"Red Team", value=f"1. {redPlayer1}"
                                            f"\n2. {redPlayer2}"
                                            f"\n3. {redPlayer3}"
                                            f"\n4. {redPlayer4}"
                                            f"\n5. {redPlayer5}")
    embed.add_field(name=f"Blue Team", value=f"6. {bluePlayer1}"
                                             f"\n7. {bluePlayer2}"
                                             f"\n8. {bluePlayer3}"
                                             f"\n9. {bluePlayer4}"
                                             f"\n10. {bluePlayer5}")
    await ctx.send(embed=embed)

    await ctx.send("Select a number for more player info, or type 0 for " + fullName)
    option = await get_input_of_type(int, ctx)
    if option == 0:
        fullName = fullName
    elif option == 1:
        fullName = redPlayer1
    elif option == 2:
        fullName = redPlayer2
    elif option == 3:
        fullName = redPlayer3
    elif option == 4:
        fullName = redPlayer4
    elif option == 5:
        fullName = redPlayer5
    elif option == 6:
        fullName = bluePlayer1
    elif option == 7:
        fullName = bluePlayer2
    elif option == 8:
        fullName = bluePlayer3
    elif option == 9:
        fullName = bluePlayer4
    elif option == 10:
        fullName = bluePlayer5
    else:
        await ctx.send("--> Error! Not an option <--")
        return

    playerIMG = GAMEINFO[1][fullName]["agent_image_url"]
    agent = GAMEINFO[1][fullName]["agent"]
    rank = GAMEINFO[1][fullName]["rank"]
    kills = GAMEINFO[1][fullName]["kills"]
    deaths = GAMEINFO[1][fullName]["deaths"]
    assists = GAMEINFO[1][fullName]["assists"]
    kd = GAMEINFO[1][fullName]["kd_ratio"]
    score = GAMEINFO[1][fullName]["score"]

    mainPlayerEmbed = discord.Embed()
    mainPlayerEmbed.set_thumbnail(url=playerIMG)
    mainPlayerEmbed.set_author(name=f"{fullName} stats")
    mainPlayerEmbed.add_field(name=f"This player played {agent}", value=f"Rank: **{rank}**")
    mainPlayerEmbed.add_field(name=f"Gameplay stats:", value=f"Score: {score}"
                                                             f"\nKills: {kills}"
                                                             f"\nAssists: {assists}"
                                                             f"\nDeaths: {deaths}"
                                                             f"\nOverall KD: {kd}")
    await ctx.send(embed=mainPlayerEmbed)


async def matches_unrated(ctx, riotName, riotID):
    msg = await ctx.send("--> Getting Match stats <--")
    history_api = f"https://api.henrikdev.xyz/valorant/v1/account/{riotName}/{riotID}"
    async with aiohttp.ClientSession() as session:
        async with session.get(history_api) as r:
            data = json.loads(await r.text())

    fullName = riotName + "#" + riotID

    puuid = data["data"]["puuid"]
    await msg.edit(content=f"--> Player ID: {puuid}")
    history = valclient.fetch_match_history(puuid=puuid, queue_id="unrated")
    matchID = history["History"][0]["MatchID"]
    await msg.edit(content=f"--> Last Unrated Match ID: {matchID}")
    GAMEINFO = await match_stats(match_id=matchID)
    await msg.edit(content=f"--> Successfully got last match details! <--")

    map_name = GAMEINFO[0]["match_info"]["map_name"]
    map_URL = GAMEINFO[0]["match_info"]["map_image_url"]
    RedPoints = GAMEINFO[0]["Red"]["rounds_won"]
    BluePoints = GAMEINFO[0]["Blue"]["rounds_won"]
    date = GAMEINFO[0]["match_info"]["start"]
    substring = "T"
    if substring in date:
        date = date.split('T')

    dateDay = date[0]
    dateTime = date[1]

    substring = "."
    if substring in dateTime:
        dateTime = dateTime.split('.')

    duration = float(GAMEINFO[0]["match_info"]["duration"])
    duration = duration / 60000
    duration = "{:.2f}".format(duration)
    players = GAMEINFO[1]
    blueTeam = []
    redTeam = []

    for players in players:
        if GAMEINFO[1][players]["team"] == "Blue":
            blueTeam.append(players)
        else:
            redTeam.append(players)

    redPlayer1 = redTeam[0]
    redPlayer2 = redTeam[1]
    redPlayer3 = redTeam[2]
    redPlayer4 = redTeam[3]
    redPlayer5 = redTeam[4]

    bluePlayer1 = blueTeam[0]
    bluePlayer2 = blueTeam[1]
    bluePlayer3 = blueTeam[2]
    bluePlayer4 = blueTeam[3]
    bluePlayer5 = blueTeam[4]

    embed = discord.Embed()
    embed.set_thumbnail(url=map_URL)
    embed.set_author(name=f"Match details for {riotName} (Unrated)")
    embed.add_field(name=f"Map", value=map_name)
    embed.add_field(name=f"Duration", value=f"{duration} minutes")
    embed.add_field(name=f"Date", value=f"On {dateDay} at {dateTime[0]}")
    embed.add_field(name="Points", value=f"Red : Blue\n{RedPoints} : {BluePoints}")
    embed.add_field(name=f"Red Team", value=f"1. {redPlayer1}"
                                            f"\n2. {redPlayer2}"
                                            f"\n3. {redPlayer3}"
                                            f"\n4. {redPlayer4}"
                                            f"\n5. {redPlayer5}")
    embed.add_field(name=f"Blue Team", value=f"6. {bluePlayer1}"
                                             f"\n7. {bluePlayer2}"
                                             f"\n8. {bluePlayer3}"
                                             f"\n9. {bluePlayer4}"
                                             f"\n10. {bluePlayer5}")
    await ctx.send(embed=embed)

    await ctx.send("Select a number for more player info, or type 0 for " + fullName)
    option = await get_input_of_type(int, ctx)
    if option == 0:
        fullName = fullName
    elif option == 1:
        fullName = redPlayer1
    elif option == 2:
        fullName = redPlayer2
    elif option == 3:
        fullName = redPlayer3
    elif option == 4:
        fullName = redPlayer4
    elif option == 5:
        fullName = redPlayer5
    elif option == 6:
        fullName = bluePlayer1
    elif option == 7:
        fullName = bluePlayer2
    elif option == 8:
        fullName = bluePlayer3
    elif option == 9:
        fullName = bluePlayer4
    elif option == 10:
        fullName = bluePlayer5
    else:
        await ctx.send("--> Error! Not an option <--")
        return

    playerIMG = GAMEINFO[1][fullName]["agent_image_url"]
    agent = GAMEINFO[1][fullName]["agent"]
    # rank = GAMEINFO[1][fullName]["rank"]
    kills = GAMEINFO[1][fullName]["kills"]
    deaths = GAMEINFO[1][fullName]["deaths"]
    assists = GAMEINFO[1][fullName]["assists"]
    kd = GAMEINFO[1][fullName]["kd_ratio"]
    score = GAMEINFO[1][fullName]["score"]

    mainPlayerEmbed = discord.Embed()
    mainPlayerEmbed.set_thumbnail(url=playerIMG)
    mainPlayerEmbed.set_author(name=f"{fullName} stats")
    mainPlayerEmbed.add_field(name=f"This player played", value=f"{agent}")
    mainPlayerEmbed.add_field(name=f"Gameplay stats:", value=f"Score: {score}"
                                                             f"\nKills: {kills}"
                                                             f"\nAssists: {assists}"
                                                             f"\nDeaths: {deaths}"
                                                             f"\nOverall KD: {kd}")
    await ctx.send(embed=mainPlayerEmbed)


async def match_stats(match_id):
    match_api = f"https://api.tracker.gg/api/v2/valorant/rap-matches/{match_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(match_api, json={}) as r:
            data = (await r.json())["data"]

    MATCH_DATA = {}
    PLAYER_DATA = {}

    red_team = data["segments"][0]
    blue_team = data["segments"][1]
    players = data["segments"][2:12]

    MATCH_DATA["match_info"] = {}
    MATCH_DATA["match_info"]["duration"] = data["metadata"]["duration"]
    MATCH_DATA["match_info"]["start"] = data["metadata"]["dateStarted"]
    MATCH_DATA["match_info"]["map_name"] = data["metadata"]["mapName"]
    MATCH_DATA["match_info"]["map_image_url"] = data["metadata"]["mapImageUrl"]

    MATCH_DATA["Red"] = {}
    MATCH_DATA["Red"]["rounds_won"] = red_team["stats"]["roundsWon"]["displayValue"]
    MATCH_DATA["Red"]["won"] = red_team["metadata"]["hasWon"]

    MATCH_DATA["Blue"] = {}
    MATCH_DATA["Blue"]["rounds_won"] = blue_team["stats"]["roundsWon"]["displayValue"]
    MATCH_DATA["Blue"]["won"] = blue_team["metadata"]["hasWon"]

    for player in players:
        metadata = player["metadata"]
        display_name = metadata["platformInfo"]["platformUserIdentifier"]
        team = metadata["teamId"]
        agent = metadata["agentName"]
        agentImageUrl = metadata["agentImageUrl"]

        stats = player["stats"]
        rank = stats["rank"]["displayValue"]
        score = stats["scorePerRound"]["displayValue"]
        kills = stats["kills"]["displayValue"]
        deaths = stats["deaths"]["displayValue"]
        assists = stats["assists"]["displayValue"]
        kdRatio = stats["kdRatio"]["displayValue"]
        damagePerRound = stats["damagePerRound"]["displayValue"]

        PLAYER_DATA[display_name] = {}
        PLAYER_DATA[display_name]["team"] = team
        PLAYER_DATA[display_name]["agent"] = agent
        PLAYER_DATA[display_name]["agent_image_url"] = agentImageUrl
        PLAYER_DATA[display_name]["rank"] = rank
        PLAYER_DATA[display_name]["score"] = score
        PLAYER_DATA[display_name]["kills"] = kills
        PLAYER_DATA[display_name]["deaths"] = deaths
        PLAYER_DATA[display_name]["assists"] = assists
        PLAYER_DATA[display_name]["kd_ratio"] = kdRatio

    return MATCH_DATA, PLAYER_DATA


print("Connecting to discord...")

client.run(TOKEN, reconnect=True)
