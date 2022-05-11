import discord
from discord.ext import tasks, commands
import aiohttp
from bs4 import BeautifulSoup
import lxml
import motor.motor_asyncio
import dateutil.parser as dt

def read_line(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        return lines[0].strip()

DEFAULT_PREFIX = '!'
TOKEN = read_line('token.txt')

PASSWORD = read_line('password.txt')
Cluster = motor.motor_asyncio.AsyncIOMotorClient(f'mongodb+srv://ItsMeNoodle:{PASSWORD}@cluster0.vkzgf.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = Cluster['ZSMEIEbot']
collection = db['ZSMEIEbot']

async def get_prefix(bot, message):
    prefix = (await collection.find_one({'guild_id':message.guild.id}))['prefix']
    return commands.when_mentioned_or(prefix)(bot, message)

intents = discord.Intents.default()
intents.guilds = True
bot = commands.Bot(command_prefix = get_prefix, intents=intents)

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')

    guild_ids = await collection.distinct("guild_id")
    task.start(guild_ids)

@bot.event
async def on_guild_join(guild):
        data = {'guild_id':guild.id,'prefix':DEFAULT_PREFIX,'announcements_channel_id':'','articles':[]}
        await collection.insert_one(data)

@bot.event
async def on_guild_remove(guild):
    await collection.delete_one({'guild_id':guild.id})

@bot.event  
async def on_guild_channel_delete(channel):
    if (await collection.find_one({'guild_id':channel.guild.id}))['announcements_channel_id'] == channel.id:
        await collection.update_one({'guild_id':channel.guild.id}, {'$set':{'announcements_channel_id':''}})

async def scrap_announcements(guild_id):
    channel_id = (await collection.find_one({'guild_id':guild_id}))['announcements_channel_id']
    if channel_id is not None:
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://zsmeie.torun.pl/') as r:
                source = await r.text()
                soup = BeautifulSoup(source, 'lxml')
                articles = soup.find_all('article')
                articles.reverse()
                for article in articles:
                    header = article.header.h2.a.text
                    try:
                        datestr = article.find(class_='entry-date published')['datetime']
                    except:
                        datestr = article.find(class_='entry-date published updated')['datetime']
                    content = article.find(class_='entry-content').p.text if article.find(class_='entry-content').p is not None else '\u200B'
                    link = article.header.h2.a['href']

                    article_dict = {'header':header,'date':datestr,'content':content,'link':link}

                    if article_dict not in (await collection.find_one({'guild_id':guild_id}))['articles']:
                        await collection.update_one({'guild_id':guild_id},{'$push':{'articles':article_dict}})
                        
                        date = dt.parse(datestr)
                        embed = discord.Embed(title=header, url=link, timestamp = date, colour=0xFFC857)
                        embed.add_field(name='\u200B', value=content)
                        await bot.get_channel(channel_id).send(embed=embed)

@bot.command()
@commands.guild_only()
async def ogloszenia(ctx):
    await ctx.message.delete()
    await scrap_announcements(ctx.guild.id)

@bot.command()
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def kanalogloszeniowy(ctx, channel_id = None):
    try:
        if channel_id is None:
            channel_id = int(ctx.channel.id)
        await ctx.message.delete()
        await collection.update_one({'guild_id':ctx.guild.id}, {'$set':{'announcements_channel_id':channel_id}})
        await collection.update_one({'guild_id':ctx.guild.id}, {'$set':{'articles':[]}})
        await scrap_announcements(ctx.guild.id)
        
    except:
        await ctx.send(f'Błąd: {channel_id} nie jest ID żadnego kanału.')

@bot.command()
async def plan(ctx, class_='2p'):
    try:
        await ctx.send(file=discord.File(f'plany/{class_.lower()}.png'))
    except FileNotFoundError:
        await ctx.send('Niepoprawna nazwa klasy!')

@bot.command()
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def prefix(ctx, new_prefix):
    await collection.update_one({'guild_id':ctx.guild.id}, {'$set':{'prefix':new_prefix}})
    await ctx.send(f'Prefix ustawiony na {new_prefix}')

@tasks.loop(minutes=10)
async def task(guild_ids):
    for guild_id in guild_ids:
        await scrap_announcements(guild_id)

bot.run(TOKEN)
