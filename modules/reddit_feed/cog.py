import os
import datetime
import time

from dotenv.main import load_dotenv

from discord.ext.tasks import loop
from discord.ext import commands

import asyncpraw
from asyncprawcore.exceptions import AsyncPrawcoreException
import asyncpraw.exceptions

from modules.reddit_feed.reddit_post import RedditPost

load_dotenv()

# Test Server
DISCORD_GUILD = int(os.getenv("DISCORD_GUILD"))

# Reddit credentials
ME = os.getenv("REDDIT_USERNAME")
PASSWORD = os.getenv("REDDIT_PASSWORD")
SUB = os.getenv("REDDIT_SUB")
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")

# Reddit feed settings
CHECK_INTERVAL = 5  # seconds to wait before checking again
SUBMISSION_LIMIT = 5  # number of submissions to check

# initialize AsyncPraw reddit api
reddit = asyncpraw.Reddit(
	client_id=CLIENT_ID,
	client_secret=CLIENT_SECRET,
	password=PASSWORD,
	user_agent=f"{ME} Bot",
	username=ME,
)


class RedditFeedCog(commands.Cog, name="Reddit Feed"):
	"""Checks for `resend` command and starts Reddit feed loop to check submissions"""

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		"""When discord is connected"""
		# Start Reddit loop
		self.reddit_feed.start()

	def is_in_guild(guild_id):
		"""check that command is in a guild"""

		async def predicate(ctx):
			return ctx.guild and ctx.guild.id == guild_id

		return commands.check(predicate)

	@commands.command(name="resend")
	@commands.has_permissions(administrator=True)
	@is_in_guild(DISCORD_GUILD)
	async def resend(self, ctx):
		"""Command to resend the last post again.
		Invoked with !resend"""
		# log command in console
		print("Received resend command")
		# respond to command
		await ctx.send("Resending last announcement!")
		# check for last submission in subreddit
		subreddit = await reddit.subreddit(SUB)
		async for submission in subreddit.new(limit=1):
			# process submission
			await RedditPost(self.bot, submission).process_post()

	@loop(seconds=CHECK_INTERVAL)
	async def reddit_feed(self):
		"""loop every few seconds to check for new submissions"""
		try:
			# check for new submission in subreddit
			subreddit = await reddit.subreddit(SUB)
			async for submission in subreddit.new(limit=SUBMISSION_LIMIT):
				# check if the post has been seen before
				if not submission.saved:
					# save post to mark as seen
					submission.save()
					# process submission
					await RedditPost(self.bot, submission).process_post()
		except AsyncPrawcoreException as err:
			print(f"EXCEPTION: AsyncPrawcoreException. {err}")
			time.sleep(10)
		except Exception as err:
			print(f"EXCEPTION: An error occured. {err}")
			time.sleep(10)

	@reddit_feed.before_loop
	async def reddit_feed_init(self):
		"""print startup info before reddit feed loop begins"""
		print(f"Logged in: {str(datetime.datetime.now())[:-7]}")
		print(f"Timezone: {time.tzname[time.localtime().tm_isdst]}")
		print(f"Subreddit: {SUB}")
		print(f"Checking {SUBMISSION_LIMIT} posts every {CHECK_INTERVAL} seconds")


def setup(bot):
	bot.add_cog(RedditFeedCog(bot))
