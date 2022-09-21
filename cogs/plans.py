import os
import discord
from discord.ext import commands
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv


class PlansCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        with open('klasy.json', 'r') as f:
            self.klasy = json.load(f)


    @commands.command(name='plan')
    async def plan(self, ctx, klasa='3P'):
        async with ctx.typing():
            file = await self.scrap_plan(klasa)
        if not file:
            await ctx.send('Nie znaleziono klasy!')
            return
        await ctx.send(file=file)


    async def scrap_plan(self, klasa):
        o_part = self.klasy.get(klasa.upper())
        if not o_part:
            return None
        
        options = webdriver.ChromeOptions()
        load_dotenv()
        options.binary_location = os.getenv('GOOGLE_CHROME_BIN')
        options.add_argument("--headless")
        driver = webdriver.Chrome(executable_path=os.getenv("CHROMEDRIVER_PATH") ,options=options)

        driver.get(f"https://zsmeie.torun.pl/plan/plany/{o_part}.html")
        element = driver.find_element(By.CSS_SELECTOR, "body > div:nth-child(2) > table > tbody > tr:nth-child(1) > td > table > tbody")
        element.screenshot('plan.png')
        driver.close()
        file = discord.File('plan.png')
        return file


async def setup(bot: commands.Bot):
    await bot.add_cog(PlansCog(bot))
