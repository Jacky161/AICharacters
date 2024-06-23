import asyncio
import discord
from discord.ext import commands


class TestCommands(commands.Cog):
    def __init__(self, bot):
        print("[TestCommands Cog] Initializing!")
        self.bot = bot

    test_cmdgrp = discord.SlashCommandGroup("test", "Test Commands")

    @test_cmdgrp.command(name="test")
    async def test_embeds(self, ctx: discord.ApplicationContext):
        lipsum1000 = r"Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. N"
        embed = discord.Embed(title="", colour=discord.Colour.blurple())

        for i in range(6):
            embed.add_field(name="", value=lipsum1000, inline=False)

        embeds = [embed]

        await ctx.respond(embeds=embeds)

    @test_cmdgrp.command(name="sleeptest")
    async def test_sleep(self, ctx: discord.ApplicationContext):
        await ctx.defer()

        await asyncio.sleep(5)

        await ctx.respond("hi")
        await asyncio.sleep(1)
        await ctx.respond("hi again")


def setup(bot):  # this is called by Pycord to set up the cog
    bot.add_cog(TestCommands(bot))  # add the cog to the bot
