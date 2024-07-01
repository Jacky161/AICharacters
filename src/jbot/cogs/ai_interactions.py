import os
import dotenv
import openai
import discord
from typing import Optional
from discord.ext import commands
from ...llm import RemoteLLMManager
from ..helper_functions import *


class AIInteractions(commands.Cog):
    def __init__(self, bot):
        print("[AIInteractions Cog] Initializing!")
        self.bot = bot
        dotenv.load_dotenv(dotenv.find_dotenv())

        # Variables to connect to LLM API
        llm_model: str = str(os.getenv("AI_LLM_MODEL"))
        api_key: str = str(os.getenv("AI_API_KEY"))
        api_url: str = str(os.getenv("AI_API_URL"))
        system_message: Optional[str] = os.getenv("AI_SYSTEM_MESSAGE")
        verbose: bool = bool(os.getenv("AI_VERBOSE"))
        n_ctx: int = int(os.getenv("AI_n_ctx"))

        # TODO: Make each user have their own LLMManager
        self._llm: RemoteLLMManager = RemoteLLMManager(llm_model, api_key, api_url,
                                                       system_message=system_message, verbose=verbose, n_ctx=n_ctx)

    ai_cmdgrp = discord.SlashCommandGroup("ai", "AI Interactions")

    @ai_cmdgrp.command(name="prompt", description="Talk to an LLM with your own prompt.")
    async def basic_prompt_modal(self, ctx: discord.ApplicationContext):
        modal = BasicPrompt(title="AI Prompt Modal", llm=self._llm)
        await ctx.send_modal(modal)


class BasicPrompt(discord.ui.Modal):
    def __init__(self, llm: RemoteLLMManager, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._llm: RemoteLLMManager = llm
        self.add_item(discord.ui.InputText(label="Your prompt:", style=discord.InputTextStyle.long, max_length=1024))

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        try:
            ai_response = self._llm.ask(self.children[0].value)
        except openai.APIConnectionError:
            await interaction.respond(content="❌ ERROR: AI API is down.")
            return
        except Exception as e:
            await interaction.respond(content="❌ ERROR: An unknown error occurred.")
            print(f"[ERROR] An unknown error has occurred! {e}")
            return

        # Get our embed strings
        embed_strs = paragraph_split(ai_response[0])

        # Add our chunks until we hit 6k limit
        embed_title: str = "AI Response"
        prompt_str: str = "Prompt:"
        answer_str: str = "Answer:"

        # Add prompt text and the answer title first
        embeds = [discord.Embed(title=embed_title, colour=discord.Colour.blurple())]
        embeds[0].add_field(name=prompt_str, value=self.children[0].value, inline=False)

        max_embed_length: int = 6000
        max_fields: int = 25
        total_fields: int = 1
        total_characters: int = len(self.children[0].value) + len(embed_title) + len(prompt_str) + len(answer_str)
        cur_idx: int = 0

        # Process all embed strings
        while len(embed_strs) > 0:
            # Keep adding fields until we hit the max length of 6k characters or 25 fields
            if total_characters + len(embed_strs[0]) < max_embed_length and total_fields < max_fields:
                total_characters += len(embed_strs[0])
                total_fields += 1

                # First chunk of AI Response will always have "Answer:" as the title
                if cur_idx == 0 and total_fields == 2:
                    name: str = answer_str
                else:
                    name: str = ""

                embeds[cur_idx].add_field(name=name, value=embed_strs.pop(0), inline=False)

            else:
                # Add a new embed and go to the next
                embeds.append(discord.Embed(title="", colour=discord.Colour.blurple()))
                cur_idx += 1
                total_fields = 0
                total_characters = 0

        # Send first embed
        await interaction.respond(embed=embeds[0])

        # Send the rest if we have any
        if len(embeds) > 1:
            # Need to send the rest as individual messages
            for i in range(1, len(embeds)):
                await interaction.respond(embed=embeds[i])


def setup(bot):  # this is called by Pycord to set up the cog
    bot.add_cog(AIInteractions(bot))  # add the cog to the bot
