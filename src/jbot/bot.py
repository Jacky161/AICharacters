import os
import dotenv
from typing import Optional
from discord.ext import commands


class JAIBot(commands.Bot):
    VALID_COMMANDS = ["admin_msg"]

    def __init__(self):
        super().__init__()

        dotenv.load_dotenv(dotenv.find_dotenv())
        self._admin_channel = int(os.getenv("ADMIN_MSG_CHANNEL"))

    async def on_ready(self):
        print(f"Logged in as {self.user.name} ID: {self.user.id}")

    # BEGIN SOCKET COMMANDS
    async def admin_msg(self, message: str, channel: Optional[int]):
        if channel is None:
            channel = self._admin_channel

        channel = self.get_channel(channel)
        await channel.send(message)
