import re
from datetime import datetime, timedelta
from typing import Optional

import discord
import pytz
from utils.dates import format_date, parse_date

command_regex = re.compile(r"!!([\w :,\.\-\/]+)!!")


countdown_regex = re.compile(
    r"\*\*(?:(?P<hours>\d+?) hours? and )?(?P<minutes>\d+?) minutes?\*\*"
)

date_in_countdown_regex = re.compile(r"\(Countdown to ([\w :,\.\-\/]+)\)")


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
    # round up to the next minute
    seconds = int(td.total_seconds() + 59)
    # only display difference if it's positive
    hrs, mins = 0, 0
    if seconds > 0:
        hrs, mins = seconds // 3600, (seconds // 60) % 60
    output = "**"
    if hrs > 0:
        # display hours if it's greater than 0
        output += f"{hrs} {'hours' if hrs != 1 else 'hour'} and "
    # display minutes
    output += f"{mins} {'minutes' if mins != 1 else 'minute'}**"
    return output


def get_timedelta(date: datetime) -> timedelta:
    tz = date.tzinfo if date.tzinfo else pytz.timezone("US/Eastern")
    now = datetime.now().astimezone(tz)
    date = date.astimezone(tz)
    return date - now


def get_updated_content(message: discord.Message) -> str:
    match = date_in_countdown_regex.search(message.content)
    if not match:
        print("Date match not found")
        return message.content
    date = parse_date(date_str=match.group(1))
    if not isinstance(date, datetime):
        raise ValueError("An error occurred while updating countdown.")
    td = get_timedelta(date)
    countdown = format_timedelta(td)
    return countdown_regex.sub(countdown, message.content)


async def create_countdown(message: discord.Message) -> discord.Message:
    match = command_regex.search(message.content)
    date = parse_date(
        date_str=match.group(1),
        base=datetime.combine(datetime.today(), datetime.min.time()),
        future=True,
    )
    if not isinstance(date, datetime):
        return await message.channel.send("An error occurred while creating countdown.")
    td = get_timedelta(date)
    countdown = format_timedelta(td)
    content = (
        command_regex.sub(countdown, message.content)
        + f"\n\n(Countdown to {format_date(date)})"
    )
    countdown_message = await message.channel.send(content=content)
    await message.delete()
    return countdown_message
