from .aceattorney import AceAttorney

async def setup(bot):
    await bot.add_cog(AceAttorney(bot))