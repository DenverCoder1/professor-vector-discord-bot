import os
import re
import datetime
import time

from dotenv import load_dotenv
from discord.ext.tasks import loop
from discord.ext.commands import Bot

import praw
from prawcore.exceptions import PrawcoreException
import praw.exceptions

load_dotenv()

# Discord setup
TOKEN = os.getenv('DISCORD_TOKEN')
ANNOUCEMENTS_CHANNEL = int(os.getenv('DISCORD_ANNOUNCEMENTS'))
client = Bot('!')

# Reddit credentials
ME = os.getenv('REDDIT_USERNAME')
PASSWORD = os.getenv('REDDIT_PASSWORD')
SUB = os.getenv('REDDIT_SUB')
CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')

# Reddit feed settings
CHECK_INTERVAL = 5  # seconds to wait before checking again
SUBMISSION_LIMIT = 3  # number of submissions to check

# initialize praw reddit api
reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                     password=PASSWORD, user_agent=f'{ME} Bot', username=ME)


@client.event
async def on_ready():
    '''When discord is connected'''
    print(f'{client.user.name} has connected to Discord!')


@client.event
async def on_error(event, *args, **kwargs):
    '''when an exception is raised'''
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            f.write(f'Event: {event}\nMessage: {args}\n')


@client.command(pass_context=True)
async def resend(ctx):
    # log command in console
    print("Received resend command")
    # respond to command
    await ctx.send("Resending last announcement!")
    # check for last submission in subreddit
    for submission in reddit.subreddit(SUB).new(limit=1):
        # process submission
        await process_post(submission)


async def announce(message):
    '''send message in announcements channel'''
    channel = client.get_channel(ANNOUCEMENTS_CHANNEL)
    await channel.send(message)


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
    default = "🧩"  # default if no keywords are found
    keywords = {
        "results": "📊",
        "announcements": "📢"
    }
    for keyword in keywords.keys():
        if (keyword in str(post.title).lower()):
            return keywords[keyword]
    else:
        return default


def format_markdown(text):
    '''apply replacements to markdown for better Discord readability'''

    def format_headings(text):
        '''substitute headings like `### title` with TITLE'''
        def transform_title(match):
            '''transform matched group to uppercase'''
            return match.group(1).upper()
        return re.sub(r"#+[ \t]*(.*?\n)", transform_title, text)

    def format_links(text):
        '''substitute links like `[link](url)` with `link (url)`'''
        return re.sub(r"\[(.*?)\]\((.*?)\)", "\\1 (\\2)", text)

    def remove_line_breaks(text):
        '''remove line breaks like `----`'''
        return re.sub(r"\s+[\-]{4,}\s+", "\n\n", text)

    return format_headings(format_links(remove_line_breaks(text)))


def build_message(post):
    '''build message from post'''
    # get url and selftext
    emoji = get_emoji(post)
    title = post.title
    url = f'https://www.reddit.com/r/{post.subreddit}/comments/{post.id}'
    selftext = format_markdown(post.selftext)
    # trim text if over 500 characters
    if (len(selftext) > 500):
        selftext = selftext[:500] + '...'
    # hide selftext in announcements
    if ("announcements" in post.title.lower()):
        selftext = ""
    return f"{emoji}  |  **{title}**\n\n{url}\n\n{selftext}"


async def process_post(post):
    '''check post and announce if not saved'''
    # log post details in console
    print(f"Recieved post by {post.author} at {get_date(post)}")
    # create message with url and text
    message = build_message(post)
    # send to discord announcements
    await announce(message)
    # log announcement status in console
    print(f"Sent announcement.")

# Start Reddit loop
reddit_feed.start()

# Run Discord bot
client.run(TOKEN)
