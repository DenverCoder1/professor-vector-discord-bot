import os
import discord
from dotenv import load_dotenv

import praw
import datetime
import time
from prawcore.exceptions import PrawcoreException
import praw.exceptions

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
ANNOUCEMENTS_CHANNEL = int(os.getenv('DISCORD_ANNOUNCEMENTS'))

client = discord.Client()


@client.event
async def on_ready():
    '''When discord is connected'''
    print(f'{client.user.name} has connected to Discord!')
    # connect to reddit
    await begin_checking_reddit()


@client.event
async def on_error(event, *args, **kwargs):
    '''when an exception is raised'''
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            f.write(f'Event: {event}\nMessage: {args[0]}\n')


async def announce(message):
    '''send message in announcements channel'''
    channel = client.get_channel(ANNOUCEMENTS_CHANNEL)
    await channel.send(message)

# REDDIT FEED

# Reddit credentials
ME = os.getenv('REDDIT_USERNAME')
PASSWORD = os.getenv('REDDIT_PASSWORD')
SUB = os.getenv('REDDIT_SUB')
CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')

# Reddit feed settings
CHECK_INTERVAL = 5  # seconds to wait before checking again
SUBMISSION_LIMIT = 5  # number of submissions to check

# initialize praw
reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                     password=PASSWORD, user_agent=f'{ME} Bot',
                     username=ME)


async def begin_checking_reddit():
    '''start reddit feed loop'''
    print(f"Logged in: {str(datetime.datetime.now())[:-7]}")
    print(f"Timezone: {time.tzname[time.localtime().tm_isdst]}")
    print(f"Subreddit: {SUB}")
    print(f"Checking {SUBMISSION_LIMIT} posts every {CHECK_INTERVAL}s")
    while True:
        try:
            # check for new submission in subreddit
            for submission in reddit.subreddit(SUB).new(limit=SUBMISSION_LIMIT):
                # process submission
                await process_post(submission)
            # wait a few seconds before checking again
            time.sleep(CHECK_INTERVAL)
        except PrawcoreException as err:
            print(f"EXCEPTION: PrawcoreException. {err}")
            time.sleep(10)
        except Exception as err:
            print(f"EXCEPTION: An error occured. {err}")
            time.sleep(10)


def get_date(post):
    '''convert post date to readable timestamp'''
    time = post.created_utc
    return datetime.datetime.fromtimestamp(time)

def get_emoji(post):
    default = "🧩"
    keywords = {
        "results": "📊",
    }
    for keyword in keywords.keys():
        if (keyword in str(post.title).lower()):
            return keywords[keyword]
    else:
        return default

def build_message(post):
    '''build message from post'''
    # get url and selftext
    emoji = get_emoji(post)
    title = post.title
    url = f'https://www.reddit.com/r/{post.subreddit}/comments/{post.id}'
    selftext = post.selftext
    # trim text if over 1000 characters
    if (len(selftext) > 500):
        selftext = post.selftext[:500] + '...'
    return f"{emoji} | **{title}**\n\n{url}\n\n{selftext}"


async def process_post(post):
    '''check post and announce if not saved'''
    # check if the post has been seen before
    if (not post.saved):
        # save post to mark as seen
        post.save()
        print(f"Recieved post by {post.author} at {get_date(post)}")
        # create message with url and text
        message = build_message(post)
        # send to discord announcements
        await announce(message)
        # log details in console
        print(f"Sent announcement.")

# Run Discord bot
client.run(TOKEN)
