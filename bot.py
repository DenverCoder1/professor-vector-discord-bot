import os
import re
import datetime
import time

import discord
from dotenv import load_dotenv
from discord.ext.tasks import loop
from discord.ext.commands import Bot
from discord.ext import commands

import praw
from prawcore.exceptions import PrawcoreException
import praw.exceptions

load_dotenv()

# Discord setup
TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_GUILD = int(os.getenv('DISCORD_GUILD'))
ANNOUNCEMENTS_CHANNEL = int(os.getenv('DISCORD_ANNOUNCEMENTS'))
client = Bot('!')

# Reddit credentials
ME = os.getenv('REDDIT_USERNAME')
PASSWORD = os.getenv('REDDIT_PASSWORD')
SUB = os.getenv('REDDIT_SUB')
CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')

# Reddit feed settings
CHECK_INTERVAL = 5  # seconds to wait before checking again
SUBMISSION_LIMIT = 5  # number of submissions to check

# initialize praw reddit api
reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                     password=PASSWORD, user_agent=f'{ME} Bot', username=ME)


@client.event
async def on_ready():
    '''When discord is connected'''
    print(f'{client.user.name} has connected to Discord!')
    # Start Reddit loop
    reddit_feed.start()


@client.event
async def on_error(event, *args, **kwargs):
    '''when an exception is raised'''
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            f.write(f'Event: {event}\nMessage: {args}\n')


def is_in_guild(guild_id):
    '''check that command is in a guild'''
    async def predicate(ctx):
        return ctx.guild and ctx.guild.id == guild_id
    return commands.check(predicate)


@client.command(pass_context=True)
@commands.has_permissions(administrator=True)
@is_in_guild(DISCORD_GUILD)
async def resend(ctx):
    '''Command to resend the last post again.
       Invoked with !resend'''
    # log command in console
    print("Received resend command")
    # respond to command
    await ctx.send("Resending last announcement!")
    # check for last submission in subreddit
    for submission in reddit.subreddit(SUB).new(limit=1):
        # process submission
        await process_post(submission)


async def announce(title, message):
    '''send message in announcements channel'''
    channel = client.get_channel(ANNOUNCEMENTS_CHANNEL)
    embed = discord.Embed(title=title, description=message)
    await channel.send(embed=embed)


@loop(seconds=CHECK_INTERVAL)
async def reddit_feed():
    '''loop every few seconds to check for new submissions'''
    try:
        # check for new submission in subreddit
        for submission in reddit.subreddit(SUB).new(limit=SUBMISSION_LIMIT):
            # check if the post has been seen before
            if (not submission.saved):
                # save post to mark as seen
                submission.save()
                # process submission
                await process_post(submission)
    except PrawcoreException as err:
        print(f"EXCEPTION: PrawcoreException. {err}")
        time.sleep(10)
    except Exception as err:
        print(f"EXCEPTION: An error occured. {err}")
        time.sleep(10)


@reddit_feed.before_loop
async def reddit_feed_init():
    '''print startup info before reddit feed loop begins'''
    print(f"Logged in: {str(datetime.datetime.now())[:-7]}")
    print(f"Timezone: {time.tzname[time.localtime().tm_isdst]}")
    print(f"Subreddit: {SUB}")
    print(f"Checking {SUBMISSION_LIMIT} posts every {CHECK_INTERVAL} seconds")


def get_date(post):
    '''convert post date to readable timestamp'''
    time = post.created_utc
    return datetime.datetime.fromtimestamp(time)


def get_emoji(post):
    '''return emoji based on keywords in title'''
    default_emoji = "🧩"  # default if no keywords are found
    emoji = {
        "results": "📊",
        "announcements": "📢"
    }
    for keyword in emoji.keys():
        if (keyword in str(post.title).lower()):
            return emoji[keyword]
    return default_emoji


def format_selftext(post):
    '''format message based on post type'''

    def format_markdown(text):
        '''apply replacements to markdown for better Discord readability'''

        def format_headings(text):
            '''substitute headings like `### title` with TITLE'''
            def transform_title(match):
                '''transform matched group to uppercase'''
                return match.group(1).upper()
            return re.sub(r"(?:^|(?<=\n))#+[ \t]*(.*?\n)", transform_title, text)

        return format_headings(text)

    def trimText(text, limit=600):
        '''trim text if over limit of characters'''
        if (len(text) > limit):
            # trim text if over limit of characters
            return text[:limit] + '...'
        # otherwise, return original
        return text

    def formatAnnouncementsPost(post):
        '''display only theme and schedule in announcements'''
        selftext = ""
        # extract theme from post text
        themeMatch = re.findall(r"(The theme .*?: .*?)\n", post.selftext)
        if (len(themeMatch) > 0):
            selftext += themeMatch[0]
        puzzlesMatch = re.findall(
            r"(Puzzle \d)\|(\[.*?\]\(.*?\))\|(\[.*?\]\(.*?\))\|", post.selftext)
        for puzzle in puzzlesMatch:
            selftext += f"\n\n**{puzzle[0]}**\n{puzzle[1]} until {puzzle[2]}"
        return selftext

    def formatResultsPost(post):
        '''tabulate points in results post and trim'''
        selftext = post.selftext
        # find points in post text
        pointsMatch = re.findall(
            r"(?:Puzzle (\d+)|.*?Points)\|\**(\d+?)\**\|\**(\d+?)\**\|\**(\d+?)\**\|\**(\d+?)\**\|",
            post.selftext)
        # create table header
        table = [
            '+-----+-----+-----+-----+-----+',
            '|  #  |  G  |  H  |  R  |  S  |',
            '+=====+=====+=====+=====+=====+',
        ]
        # add table body
        for p in pointsMatch:
            # number for puzzles, "+" for total row
            num = p[0] if len(p[0]) > 0 else "+"
            # double row for row before totals
            divider = '+-----+-----+-----+-----+-----+' if p != pointsMatch[-2] else '+=====+=====+=====+=====+=====+'
            # add table row
            table += [
                f"|  {num}  |{p[1].rjust(4)} |{p[2].rjust(4)} |{p[3].rjust(4)} |{p[4].rjust(4)} |",
                divider
            ]
        # replace markdown table
        selftext = re.sub(
            r"\*\*Level\*\*\|(?:.|\n)*? Points\|.*\n",
            "```\n" + "\n".join(table) + "\n```",
            selftext)
        selftext = re.sub("# Current Points ", "\n# Current Points ", selftext)
        # trim text if over limit of characters
        trimLength = max(600, selftext.find("Level Results"))
        selftext = trimText(selftext, trimLength)
        return format_markdown(selftext)

    def formatPuzzlePost(post):
        '''trim puzzle post'''
        # trim text if over limit of characters
        selftext = trimText(post.selftext)
        return format_markdown(selftext)

    # format text
    default_formatter = formatPuzzlePost
    formatters = {
        "announcements": formatAnnouncementsPost,
        "results": formatResultsPost
    }
    for keyword in formatters.keys():
        if (keyword in str(post.title).lower()):
            return formatters[keyword](post)
    return default_formatter(post)


def build_message(post):
    '''build message from post'''
    # get url and selftext
    emoji = get_emoji(post)
    title = post.title
    url = f'https://www.reddit.com/r/{post.subreddit}/comments/{post.id}'
    selftext = format_selftext(post)
    # create the message
    title = f"{emoji}  |  **{title}**"
    message = f"{url}\n\n{selftext}"
    return title, message


async def process_post(post):
    '''check post and announce if not saved'''
    # log post details in console
    print(f"Recieved post by {post.author} at {get_date(post)}")
    # create message with url and text
    title, message = build_message(post)
    # send to discord announcements
    await announce(title, message)
    # log announcement status in console
    print(f"Sent announcement.")

# Run Discord bot
client.run(TOKEN)
