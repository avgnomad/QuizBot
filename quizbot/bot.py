import os
from datetime import datetime
from sys import version as sys_version

from disnake import __version__ as disnake_version
from disnake.ext import commands
from loguru import logger

from quizbot import __version__ as bot_version

__all__ = ("QuizBot",)


class QuizBot(commands.InteractionBot):
    """Base bot instance"""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    async def on_ready(self):
        """
        Function is called automatically when the bot has made
        it's connection to the Discord API

        All we will do here is print some information about the bot
        after it's successful connection.
        """

        print(
            "----------------------------------------------------------------------\n"
            f'Bot started at: {datetime.now().strftime("%m/%d/%Y - %H:%M:%S")}\n'
            f"System Version: {sys_version}\n"
            f"Disnake Version: {disnake_version}\n"
            f"Bot Version: {bot_version}\n"
            f"Connected to Discord as {self.user} ({self.user.id})\n"
            "----------------------------------------------------------------------\n"
        )

    def load_extensions(self) -> None:
        """
        Iterate the cog directory and load relevant bot extension
        modules
        """
        for item in os.listdir("quizbot/cogs"):
            if "__" in item:
                continue

            extension = f"quizbot.cogs.{item[:-3]}"
            self.load_extension(extension)
            logger.info(f"Cog loaded: {extension}")
