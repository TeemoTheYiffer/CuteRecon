from .artist import Artist


async def setup(bot):
    await bot.add_cog(Artist(bot))
