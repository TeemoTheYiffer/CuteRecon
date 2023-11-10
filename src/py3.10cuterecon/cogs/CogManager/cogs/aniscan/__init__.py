from .aniscan import Aniscan


async def setup(bot):
    await bot.add_cog(Aniscan(bot))
