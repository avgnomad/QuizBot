from typing import Optional

import disnake
from disnake.ext import commands
from quizbot import components, config
from quizbot.bot import QuizBot


class Admin(commands.Cog):
    """
    Extension for admin related commands.
    All commands in this cog require the command user
    to have Administrator permissions/be server owner
    """

    def __init__(self, bot: QuizBot) -> None:
        self.bot = bot

    async def cog_slash_command_check(self, inter: disnake.AppCmdInter) -> bool:
        """A check that is invoked for every command within this cog extension
        Returns bool that is used to decide of the command is invoked or an error is thrown"""

        member = inter.author
        return member.guild_permissions.administrator or member == inter.guild.owner

    async def cog_slash_command_error(
        self, inter: disnake.AppCmdInter, error: Exception
    ) -> None:
        """Called when any command within this cog has raised an error.  For this, we only wish
        to catch errors thrown by the cog_slash_command check returning False"""

        if isinstance(error, commands.CheckFailure):
            return await inter.response.send_message(
                f"It seems you do not have the required permissions to use this command",
                ephemeral=True,
            )

        if isinstance(error, commands.PrivateMessageOnly):
            return await inter.response.send_message(
                "This command is only useable within a guild channel", ephemeral=True
            )

        # raise any other errors
        raise error

    @commands.slash_command(name="edit")
    @commands.default_member_permissions(
        administrator=True
    )  # sets the default integration rule for this command
    @commands.guild_only()  # prevents this command from being used outside of a server
    async def config(self, interaction: disnake.AppCmdInter) -> None:
        """Config parent command.  Always invoked if any sub-commands are used"""
        pass

    @config.sub_command(name="pass_embed")
    @commands.guild_only()  # prevents this command from being used outside of a server
    async def config_correct_embed(
        self,
        inter: disnake.AppCmdInter,
        thumbnail: Optional[disnake.Attachment] = None,
        image: Optional[disnake.Attachment] = None,
        clear_images: Optional[bool] = False,
    ) -> None:
        """View and edit the "Incorrect" embed that is displayed when a user has failed the quiz

        Parameters
        ----------
        thumbnail: :type:`Optional[disnake.Attachment]`
            Optionally set the embed's thumbnail (Set 'clear_images' to True to clear the set thumbnail)
        image: :type:`Optional[disnake.Attachment]`
            Optionally set the embed's image (Set 'clear_images' to True to clear the set image))
        clear_images: :type:`bool`
            Optionally clear the image and thumbnail from the embed
        """

        embed = config.get_embed(inter.guild.id, _type="correct")
        if embed is None:
            embed = components.default_embed()

        if clear_images:
            embed.set_thumbnail(url=None)
            embed.set_image(url=None)
        else:
            embed.set_thumbnail(url=thumbnail.url if thumbnail else None)
            embed.set_image(url=image.url if image else None)

        view = components.EditEmbedButtons("correct")

        await inter.response.send_message(
            "Here is your currently configured 'Pass' embed.  You can click the buttons below to make changes, "
            "submit the changes, or cancel the change",
            embed=embed,
            ephemeral=True,
            view=view,
        )

    @config.sub_command(name="fail_embed")
    @commands.guild_only()  # prevents this command from being used outside of a server
    async def config_incorrect_embed(
        self,
        inter: disnake.AppCmdInter,
        thumbnail: Optional[disnake.Attachment] = None,
        image: Optional[disnake.Attachment] = None,
        clear_images: Optional[bool] = False,
    ) -> None:
        """View and edit the "Incorrect" embed that is displayed when a user has failed the quiz

        Parameters
        ----------
        thumbnail: :type:`Optional[disnake.Attachment]`
            Optionally set the embed's thumbnail (Set 'clear_images' to True to clear the set thumbnail)
        image: :type:`Optional[disnake.Attachment]`
            Optionally set the embed's image (Set 'clear_images' to True to clear the set image))
        clear_images: :type:`bool`
            Optionally clear the image and thumbnail from the embed
        """

        embed = config.get_embed(inter.guild.id, _type="incorrect")

        if clear_images:
            embed.set_thumbnail(url=None)
            embed.set_image(url=None)
        else:
            embed.set_thumbnail(url=thumbnail.url if thumbnail else None)
            embed.set_image(url=image.url if image else None)

        view = components.EditEmbedButtons("incorrect")

        await inter.response.send_message(
            "Here is your currently configured 'Fail' embed.  You can click the buttons below to make changes, "
            "submit the changes, or cancel the change",
            embed=embed,
            ephemeral=True,
            view=view,
        )

    @config.sub_command(name="quiz_embed")
    @commands.guild_only()  # prevents this command from being used outside of a server
    async def config_incorrect_embed(
        self,
        inter: disnake.AppCmdInter,
        thumbnail: Optional[disnake.Attachment] = None,
        image: Optional[disnake.Attachment] = None,
        clear_images: Optional[bool] = False,
    ) -> None:
        """View and edit the "Quiz" embed that will be displayed to start a quiz

        Parameters
        ----------
        thumbnail: :type:`Optional[disnake.Attachment]`
            Optionally set the embed's thumbnail (Set 'clear_images' to True to clear the set thumbnail)
        image: :type:`Optional[disnake.Attachment]`
            Optionally set the embed's image (Set 'clear_images' to True to clear the set image))
        clear_images: :type:`bool`
            Optionally clear the image and thumbnail from the embed
        """

        embed = config.get_embed(inter.guild.id, _type="quiz")

        if clear_images:
            embed.set_thumbnail(url=None)
            embed.set_image(url=None)
        else:
            embed.set_thumbnail(url=thumbnail.url if thumbnail else None)
            embed.set_image(url=image.url if image else None)

        view = components.EditEmbedButtons("quiz")

        await inter.response.send_message(
            "Here is your currently configured 'Quiz' embed.  You can click the buttons below to make changes, "
            "submit the changes, or cancel the change",
            embed=embed,
            ephemeral=True,
            view=view,
        )


def setup(bot: QuizBot) -> None:
    bot.add_cog(Admin(bot))
