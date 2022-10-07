from typing import List, Literal

import disnake

from quizbot import config

__all__ = (
    "default_embed",
    "EditEmbedButtons",
)


def default_embed() -> disnake.Embed:
    """Create a default Embed for when the guild doesn't have one setup yet"""
    embed = disnake.Embed(
        title="Example Embed Title", description="Example embed description"
    )
    return embed


class EditEmbed(disnake.ui.Modal):
    """Modal for editing the embed body"""

    embed: disnake.Embed

    def __init__(self):

        components = [
            disnake.ui.TextInput(
                label="Title",
                placeholder="Edit the title of your embed",
                style=disnake.TextInputStyle.long,
                custom_id="title",
                max_length=250,
                required=True,
            ),
            disnake.ui.TextInput(
                label="Body",
                placeholder="Edit the body of your embed",
                style=disnake.TextInputStyle.long,
                custom_id="body",
                max_length=3500,
                required=True,
            ),
        ]
        super().__init__(title="Edit Embed", components=components)

    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        """Callback for this modal"""

        title = interaction.text_values.get("title")
        body = interaction.text_values.get("body")

        embed = self.embed
        embed.title = title
        embed.description = body

        await interaction.response.edit_message(embed=embed)


class EditEmbedButtons(disnake.ui.View):

    message: disnake.Message

    def __init__(self, _type: Literal["correct", "incorrect", "quiz"]):
        super().__init__(timeout=None)
        self.type = _type

    @disnake.ui.button(label="Edit", style=disnake.ButtonStyle.primary)
    async def edit_embed(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ) -> None:
        """Callback for edit embed button"""

        modal = EditEmbed()
        modal.embed = interaction.message.embeds[0]

        return await interaction.response.send_modal(modal=modal)

    @disnake.ui.button(label="Save", style=disnake.ButtonStyle.success)
    async def save_embed(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ) -> None:
        """Callback for save embed button"""

        embed = interaction.message.embeds[0]

        await interaction.response.edit_message(
            "Your customization has been saved. You may close this message.",
            view=self.clear_items(),
        )
        self.stop()

        # save the updated embed
        config.update_embed(embed, guild_id=interaction.guild.id, _type=self.type)

        # if type is 'quiz' we also need to make sure to store the channel and message ID
        # if it doesn't already exist or update the message embed if it does exist

        if self.type == "quiz":

            message_id, channel_id = config.get_quiz_message(interaction.guild.id)

            if message_id is not None and channel_id is not None:
                try:
                    channel = interaction.guild.get_channel(channel_id)
                    message = await channel.fetch_message(message_id)
                except disnake.NotFound:
                    pass  # channel or message wasn't found, so just skip edit and create a new message

                else:
                    return await message.edit(embed=embed)

            button = [
                disnake.ui.Button(
                    label="Start Quiz",
                    style=disnake.ButtonStyle.primary,
                    custom_id="begin_quiz",
                )
            ]

            # if no message or channel ID, we'll send a new message and store the IDs here
            message = await interaction.channel.send(embed=embed, components=button)
            config.update_quiz_message(
                interaction.guild.id, interaction.channel.id, message.id
            )

    disnake.ui.button(label="Cancel", style=disnake.ButtonStyle.danger)

    async def cancel_embed(
        self, button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ) -> None:
        """Callback for cancel emebd button"""

        await interaction.response.edit_message(
            "Customization has been cancelled.", view=self.clear_items()
        )
        self.stop()
