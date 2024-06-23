import os
import dotenv
import logging
from jbot import JAIBot


COGS = [
    "src.jbot.cogs.ai_interactions",
    "src.jbot.cogs.test"
]


# Start the bot
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    dotenv.load_dotenv(dotenv.find_dotenv())

    bot = JAIBot()

    for cog in COGS:
        bot.load_extension(cog)

    bot.run(str(os.getenv("DISCORD_TOKEN")))
