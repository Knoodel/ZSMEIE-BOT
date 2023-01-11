import json
import discord
from discord.ext import tasks, commands
import aiohttp
from bs4 import BeautifulSoup
import lxml
import dateutil.parser as dt


class AnnouncementsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.owner_id = 436567326263869441
        self.task.start()

    
    async def scrap_announcements(self):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://zsmeie.torun.pl/') as r:
                source = await r.text()
                soup = BeautifulSoup(source, 'lxml')
                articles = soup.find_all('article')
                articles.reverse()
                for article in articles:
                    with open('announcements.json', 'r', encoding='UTF-8') as f:
                        posted_announcements = json.load(f)['announcements']
                    header = article.header.h2.a.text
                    try:
                        datestr = article.find(class_='entry-date published')['datetime']
                    except:
                        datestr = article.find(class_='entry-date published updated')['datetime']
                    content = article.find(class_='entry-content').p.text if article.find(class_='entry-content').p is not None else '\u200B'
                    link = article.header.h2.a['href']

                    article_dict = {'header':header,'date':datestr,'content':content,'link':link}
                    if article_dict not in posted_announcements:
                        posted_announcements.append(article_dict)
                        with open('announcements.json', 'w', encoding='UTF-8') as f:
                            json.dump({'announcements':posted_announcements}, f)
                        
                        date = dt.parse(datestr)
                        embed = discord.Embed(title=header, url=link, timestamp = date, colour=0xFFC857)
                        embed.add_field(name='\u200B', value=content)
                        await (await self.bot.fetch_user(self.owner_id)).send(embed=embed)
                        
                        
    @commands.command(name='reset')
    @commands.is_owner()
    async def reset(self, ctx):
        with open('announcements.json', 'w', encoding='UTF-8') as f:
            json.dump({"announcements": []}, f)
            await ctx.send('Wyczyszczono bazę danych!')


    @commands.command(name='ogloszenia')
    async def ogloszenia(self, ctx):
        await self.scrap_announcements()

    @tasks.loop(minutes=1)
    async def task(self):
        await self.scrap_announcements()


async def setup(bot: commands.Bot):
    await bot.add_cog(AnnouncementsCog(bot))
