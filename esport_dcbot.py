import coc
import traceback

import discord
from discord.ext import commands

from riotwatcher import LolWatcher, ApiError

# Read info at Discord Developer Portal and Clash of Clans Developer Portal before use!

'''
Store authentication info in separate file:
line 1: CoC dev username
line 2: CoC dev password
line 3: DC info channel ID
line 4: DC bot OAUTH2 token
line 5: Your clan's tag
line 6: LoL API key
'''
with open("orabot_food.txt") as f:
    auth = f.readlines()
auth = [x.strip() for x in auth] 

clan_tag = auth[4] # Tag of the clan that you want to follow.
coc_client = coc.login(auth[0], auth[1], key_count=5, key_names="Bot key", client=coc.EventsClient,)

lol_api = LolWatcher(auth[5]) # Get your API key on https://developer.riotgames.com (you have to be logged in)
my_region = "eun1"

bot = commands.Bot(command_prefix="!")
INFO_CHANNEL_ID = int(auth[2]) # ID of the info channel where the bot will post messages.

@coc_client.event
async def on_clan_member_versus_trophies_change(old_trophies, new_trophies, player):
	await bot.get_channel(INFO_CHANNEL_ID).send(
        "{0.name}-nak/nek jelenleg {1} versus trófeája van".format(player, new_trophies))

@bot.command()
async def hello(ctx):
    await ctx.send("Oh, hello there!")

@bot.command()
async def lolme(ctx):
    me = lol_api.summoner.by_name(my_region, "1lleagle")
    await ctx.send("Name: {0} (Level: {1})".format(me["name"], me["summonerLevel"]))

@bot.command()
async def lolranked(ctx, name):
    me = lol_api.summoner.by_name(my_region, name)
    my_ranked_stats = lol_api.league.by_summoner(my_region, me['id'])
    if not my_ranked_stats:
        await ctx.send("Te még nem rankedeztél!")
    else:
        data = my_ranked_stats[0]
        output = "{0} \nRanked Solo/Duo: {1} {2}\n Wins: {3} Losses: {4} \n".format(data['summonerName'], data['tier'], data['rank'], data['wins'], data["losses"])
        data = my_ranked_stats[1]
        output += "Ranked FLEX: {0} {1} \n Wins: {2} Losses: {3}".format(data['tier'], data['rank'], data['wins'], data['losses'])
        await ctx.send(output)

# @bot.command()
# async def lolf2p(ctx):
#     f2p = lol_api.rotations(my_region)
#     await ctx.send(f2p)

@bot.command()
async def parancsok(ctx):
    await ctx.send("!hello, !hosok \{player_tag\}, !tagok !lolme !lolranked")

@bot.command()
async def hosok(ctx, player_tag):
    player = await coc_client.get_player(player_tag)

    to_send = ""
    for hero in player.heroes:
        to_send += "{}: Lv {}/{}\n".format(str(hero), hero.level, hero.max_level)

    await ctx.send(to_send)

@bot.command()
async def tagok(ctx):
    members = await coc_client.get_members(clan_tag)

    to_send = "A tagok:\n"
    for player in members:
        to_send += "{0} ({1})\n".format(player.name, player.tag)

    await ctx.send(to_send)

coc_client.add_clan_update(
    [clan_tag], retry_interval=60
)
coc_client.start_updates()

bot.run(auth[3])