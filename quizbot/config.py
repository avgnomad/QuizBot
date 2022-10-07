import json
import os
from typing import Literal, Tuple

import disnake

from quizbot import components

__all__ = (
    "token",
    "required_roles",
    "update_embed",
    "get_embed",
    "get_quiz_message",
    "update_quiz_message",
    "add_to_quizzed",
    "check_quizzed_member",
)


# bot token loaded from the environment variables
token = os.getenv("TOKEN")

# required roles to start the quiz.
# list of role Ids that would be checked on_button_click
# user needs all roles in this list to start the quiz
required_roles = [1027932739502080071, 1027932777867399239]  # change examples

# role to be given on successful completion of the quiz
quiz_role = 1027932804216012881


"""
Some basic config load,
unloading and updating functions.
Do not mess with this section
"""


def load_data() -> dict[str, str]:
    """Loads all data from the json"""
    with open("quizbot/data/config.json") as f:
        return json.load(f)


def dump_data(data: dict[str, dict]) -> None:
    """Dumps the data back into the json file"""
    with open("quizbot/data/config.json", "w") as f:
        json.dump(data, f, indent=4)


def update_embed(
    embed: disnake.Embed,
    *,
    guild_id: int,
    _type: Literal["correct", "incorrect", "quiz"]
) -> None:
    """Add the updated embed to the config file"""
    data = load_data()
    guild = data.get(str(guild_id))

    if guild is None:
        data[str(guild_id)] = default_config()

    guild[_type] = embed.to_dict()
    dump_data(data)


def get_embed(
    guild_id: int, *, _type: Literal["correct", "incorrect", "quiz"]
) -> disnake.Embed:
    """Fetches the embed as dict from the config.json and converts it back to an Embed and returns it"""

    data = load_data()
    guild = data.get(str(guild_id))

    if guild is None:
        data[str(guild_id)] = default_config()
        dump_data(data)

    embed_as_dict = data[str(guild_id)][_type]
    return disnake.Embed.from_dict(embed_as_dict)


def get_quiz_message(guild_id: int) -> Tuple:

    data = load_data()
    guild = data.get(str(guild_id))

    if guild is None:
        data[str(guild_id)] = default_config()
        dump_data(data)
        return None, None

    message = data[str(guild_id)].get("quiz_message_id")
    channel = data[str(guild_id)].get("quiz_channel_id")

    return (message, channel)


def update_quiz_message(guild_id: int, channel_id: int, message_id: int) -> None:
    """Update the channel,and message stored IDs for the quiz starting message"""

    data = load_data()
    guild = data.get(str(guild_id))

    if guild is None:
        data[str(guild_id)] = default_config()

    data[str(guild_id)]["quiz_message_id"] = message_id
    data[str(guild_id)]["quiz_channel_id"] = channel_id

    dump_data(data)


def add_to_quizzed(guild_id: int, member_id: int) -> None:
    """Add the member to the quizzed members config"""
    data = load_data()
    guild = data.get(str(guild_id))

    if guild is None:
        data[str(guild_id)] = default_config()

    data[str(guild_id)]["quizzed"].append(member_id)
    dump_data(data)


def default_config():
    return {
        "quiz_message_id": None,
        "quiz_channel_id": None,
        "correct": components.default_embed().to_dict(),
        "incorrect": components.default_embed().to_dict(),
        "quiz": components.default_embed().to_dict(),
        "quizzed": [],
    }


def check_quizzed_member(guild_id: int, member_id: int) -> bool:
    """Check if the member_id exists in the list of quizzed members
    for the selected guild"""

    data = load_data()
    guild = data.get(str(guild_id))

    if guild is None:
        data[str(guild_id)] = default_config()
        dump_data(data)

    return member_id in data[str(guild_id)]["quizzed"]


def get_correct_embed(guild_id: int) -> disnake.Embed:
    """Gets the correct embed from config"""

    data = load_data()
    guild = data.get(str(guild_id))

    embed_as_dict = guild.get("correct")
    return disnake.Embed.from_dict(embed_as_dict)


def get_incorrect_embed(guild_id: int) -> disnake.Embed:
    """Gets the correct embed from config"""

    data = load_data()
    guild = data.get(str(guild_id))

    embed_as_dict = guild.get("incorrect")
    return disnake.Embed.from_dict(embed_as_dict)
