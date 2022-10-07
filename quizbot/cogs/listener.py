import datetime

import disnake
from disnake.ext import commands
from quizbot import config
from quizbot.bot import QuizBot
from quizbot.quiz import Quiz


class Listeners(commands.Cog):
    """Adds button/component listeners to the bot events"""

    def __init__(self, bot: QuizBot) -> None:
        self.bot = bot
        self.cooldown = commands.CooldownMapping.from_cooldown(
            1, 600, commands.BucketType.user
        )  # 10 minutes cooldown

    @commands.Cog.listener("on_button_click")
    async def start_quiz_button_listener(
        self, inter: disnake.MessageInteraction
    ) -> None:
        """On button click listener for the "Start Quiz" button"""

        if inter.component.custom_id != "begin_quiz":
            return

        # check if the button click has the required two roles to use this button
        roles = [inter.guild.get_role(int(role)) for role in config.required_roles]
        role_mentions = ", ".join(
            [role.mention for role in roles[:-1]] + [f"and {roles[-1].mention}"]
        )

        if not all(role in inter.author.roles for role in roles):
            return await inter.response.send_message(
                f"You must have {role_mentions} assigned to you before you can take this quiz.",
                ephemeral=True,
            )

        # check if the button clicker is currently on cooldown
        if retry_after := self.cooldown.update_rate_limit(inter):
            retry = disnake.utils.utcnow() + datetime.timedelta(seconds=retry_after)
            retry = disnake.utils.format_dt(retry, "R")
            return await inter.response.send_message(
                f"This button is on cooldown.  Please try again {retry}",
                ephemeral=True,
            )

        await inter.response.send_message(
            "Preparing quiz.  Please do not close this message", ephemeral=True
        )
        message = await inter.original_message()

        quiz = Quiz(message, inter.author)
        quiz.bot = self.bot
        await quiz.start_quiz()

        return


def setup(bot: QuizBot) -> None:
    bot.add_cog(Listeners(bot))
