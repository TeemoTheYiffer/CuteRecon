from .yiffertools import Yiffertools

async def setup(bot):
    await bot.add_cog(Yiffertools(bot))
