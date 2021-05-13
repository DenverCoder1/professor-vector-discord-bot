from datetime import datetime, timedelta
import re
from typing import Optional
from utils.dates import parse_date

import discord

command_regex = re.compile(r"!!([\w :,\.\-\/]+)!!")


countdown_regex = re.compile(
    r"\b(?P<hours>\d+?) hours? and (?P<minutes>\d+?) minutes?\b"
)


def message_has_command(message: discord.Message) -> bool:
    content: str = message.content
    return command_regex.search(content) is not None


def message_has_countdown(message: discord.Message) -> bool:
    content: str = message.content
    return countdown_regex.search(content) is not None


async def get_last_countdown(channel: discord.TextChannel) -> Optional[discord.Message]:
    """Returns last message that matches pattern"""
    async for message in channel.history(limit=20):
        message: discord.Message
        author: discord.Member = message.author
        if message_has_countdown(message) and author.bot:
            return message
    return None


def parse_timedelta(time_str):
    parts = countdown_regex.search(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)


def format_timedelta(td: timedelta) -> str:
    hrs, mins = td.seconds // 3600, (td.seconds // 60) % 60
    return f"{hrs} {'hours' if hrs != 1 else 'hour'} and {mins} {'minutes' if mins != 1 else 'minute'}"


def get_updated_content(message: discord.Message) -> str:
    last_timedelta = parse_timedelta(message.content)
    last_edited = datetime.utcnow() - (message.edited_at or message.created_at)
    new_timedelta = last_timedelta - last_edited
    countdown = format_timedelta(new_timedelta)
    return countdown_regex.sub(countdown, message.content)


async def create_countdown(message: discord.Message) -> discord.Message:
    date_str = command_regex.search(message.content).group(1)
    now = datetime.utcnow().replace(tzinfo=None)
    date = parse_date(date_str=date_str, to_tz="UTC", future=True).replace(tzinfo=None)
    td = date - now
    countdown = format_timedelta(td)
    content = command_regex.sub(countdown, message.content)
    return await message.channel.send(content=content)
