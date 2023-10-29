import json
import logging
import os
import typing

import discord
import openai

import api.storage
from . import interaction, llm

MONGODB_URL = os.environ.get("MONGODB_URL")
MONGODB_NAME = os.environ.get("MONGODB_NAME")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PERSIST = bool(os.environ.get("PERSIST", False))

openai.api_key = OPENAI_API_KEY


class ShappieClient(discord.Client):
    def __init__(self, *, intents: discord.Intents, **options: typing.Any):
        super().__init__(intents=intents, **options)
        self.tree = discord.app_commands.CommandTree(self)
        self._store = None
        if PERSIST:
            self._store = api.storage.DataStore(MONGODB_URL, MONGODB_NAME)
        self.pool = mafic.NodePool(self)
        self.loop = create_task(self.add_nodes())

        self._channel_access_config = {}
        with open("configs/channel_access.json") as f:
            # don't know best place to put this
            for guild in json.load(f):
                self._channel_access_config[guild["guild_id"]] = {
                    "allowed_channels": guild["allowed_channels"],
                    "reference_channel": guild["reference_channel"],
                }
        self.load_extension('dismusic')

    async def add_nodes(self):
        await self.pool.create_nodes(
            host="0.0.0.0",
            port=9095,
            label="MAIN",
            password=os.getenv("MAFIC_PASSWORD"),
        )

    async def setup_hook(self):
        await self.tree.sync()

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if str(payload.emoji) == "💩":
            logging.warning(payload.emoji)
            channel = self.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            with open("data/fallacies.json") as file:
                fallacies = json.load(file)

            state = await self._store.get_state()
            content = message.content
            message.content = (
                f"Determine if any logical fallacies are present "
                f'in this message: "{content}".\n'
                f"If any are present, explain which one(s) and why. "
                f"Additionally, ask a socratic question to continue "
                f"the dialogue by addressing the fallacious argument."
            )
            async with channel.typing():
                response = await llm.generate_response_message(
                    messages=[message],
                    state=state,
                    additional_context=fallacies,
                )
            await message.reply(response["content"])

        #    async def on_message(self, message: discord.Message):
        #        try:
        #            owner_name = message.guild.owner.name
        #            # send dm to 288880607780667394
        #            if message.author.id == 288880607780667394:
        #                await message.author.send(f"The server owner's name is {owner_name}.")
        #        except:
        #            pass
        bot_interaction = interaction.Interaction(
            self, message, self._store, self._channel_access_config
        )
        await bot_interaction.start()
