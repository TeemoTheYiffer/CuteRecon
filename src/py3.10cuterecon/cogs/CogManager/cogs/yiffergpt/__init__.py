from .yiffergpt import YifferGPT

async def setup(bot):
    await bot.add_cog(YifferGPT(bot))
