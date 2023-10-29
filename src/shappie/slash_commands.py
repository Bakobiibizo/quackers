import nextcord
from nextcord.ext import commands
import mafic
import os
import dotenv

from bot import ShappieClient

bot = commands.Bot(intents=nextcord.Intents.all(), command_prefix=commands.when_mentioned_or("/"))

bot.lavalink_nodes = [
    {"host": "lavalink.oryzen.xyz", "port": 1262, "password": "discord.gg/6xpF6YqVDd"},
    # Can have multiple nodes here
]
bot.spotify_credentials = {
    
    'client_id': os.environ.get('CLIENT_ID'),
    'client_secret': os.environ.get('CLIENT_SECRET'),
    
}

# No need to add the Music cog here as it will be added when the 'dismusic' extension is loaded
