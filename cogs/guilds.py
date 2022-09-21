import discord
from discord.ext import commands
from utils import get_db_col


class GuildsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.collection = get_db_col()
    
    @commands.Cog.listener('on_guild_join')
    async def on_guild_join(self, guild):
        data = {'guild_id':guild.id,'prefix':self.bot.DEFAULT_PREFIX,'announcements_channel_id':'','articles':[]}
        await self.collection.insert_one(data)


    @commands.Cog.listener('on_guild_remove')
    async def on_guild_remove(self, guild):
        await self.collection.delete_one({'guild_id':guild.id})


    @commands.Cog.listener('on_guild_channel_delete')
    async def on_guild_channel_delete(self, channel):
        guild_col = await self.collection.find_one({'guild_id':channel.guild.id})
        if guild_col['announcements_channel_id'] == channel.id:
            await self.collection.update_one({'guild_id':channel.guild.id}, {'$set':{'announcements_channel_id':''}})

    
    @commands.command(name='prefix')
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def prefix(self, ctx, new_prefix):
        await self.collection.update_one({'guild_id':ctx.guild.id}, {'$set':{'prefix':new_prefix}})
        await ctx.send(f'Prefix ustawiony na {new_prefix}')


async def setup(bot: commands.Bot):
    await bot.add_cog(GuildsCog(bot))
