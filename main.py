import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv
import os


class ZSMEIEBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='-', intents=discord.Intents.all())


    async def setup_hook(self):
        await self.load_extension('cogs.plans')
        await asyncio.sleep(1)
        print("Cogs loaded successfully!")


    async def on_ready(self):
        await self.tree.sync()
        print(f'Logged on as {self.user}!\n')


load_dotenv()
TOKEN = os.getenv('TOKEN')

bot = ZSMEIEBot()
bot.run(TOKEN)
