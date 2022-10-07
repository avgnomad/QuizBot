import asyncio
import os
import signal
import sys

from loguru import logger

try:
    import dotenv
except ModuleNotFoundError:
    pass

else:
    if dotenv.find_dotenv():
        logger.info("Found .env file, loading environment variables from it.")
        dotenv.load_dotenv(override=True)


import disnake
from loguru import logger

from quizbot import config
from quizbot.bot import QuizBot

_intents = disnake.Intents.none()
_intents.guilds = True
_intents.members = True


async def main() -> None:
    """Create the bot, load the extensions, start the bot"""

    # setting reload to true allows us to make changes within extension modules
    # and the bot will automatically reload that extension to prevent the need
    # to constantly restart the bot while making tweaks
    bot: QuizBot = QuizBot(intents=_intents, reload=True)

    try:
        bot.load_extensions()
    except Exception:
        await bot.close()
        raise

    logger.info("Bot is starting...")

    if os.name != "nt":
        # start process if not Windows based host

        loop = asyncio.get_event_loop()

        future = asyncio.ensure_future(bot.start(Config.token or ""), loop=loop)
        loop.add_signal_handler(signal.SIGINT, lambda: future.cancel())
        loop.add_signal_handler(signal.SIGTERM, lambda: future.cancel())

        try:
            await future
        except asyncio.CancelledError:

            logger.warning(
                "Kill command was sent to the bot. Closing bot and event loop"
            )
            if not bot.is_closed():
                await bot.close()
    else:
        # start bot with Windows based host
        await bot.start(config.token or "")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
