import os
import re
import datetime
import discord

ANNOUNCEMENTS_CHANNEL = int(os.getenv("DISCORD_ANNOUNCEMENTS"))


class RedditPost:
	def __init__(self, bot, post):
		self.bot = bot
		self.post = post

	async def process_post(self):
		"""check post and announce if not saved"""
		# log post details in console
		print(f"Recieved post by {self.post.author} at {self.__get_date()}")
		# create message with url and text
		title, message = self.__build_message()
		# send to discord announcements
		await self.__announce(title, message)
		# log announcement status in console
		print(f"Sent announcement.")

	async def __announce(self, title, message):
		"""send message in announcements channel"""
		channel = self.bot.get_channel(ANNOUNCEMENTS_CHANNEL)
		embed = discord.Embed(title=title, description=message)
		await channel.send(embed=embed)

	def __get_date(self):
		"""convert post date to readable timestamp"""
		time = self.post.created_utc
		return datetime.datetime.fromtimestamp(time)

	def __get_emoji(self):
		"""return emoji based on keywords in title"""
		default_emoji = "🧩"  # default if no keywords are found
		emoji = {"results": "📊", "announcements": "📢"}
		for keyword in emoji.keys():
			if keyword in str(self.post.title).lower():
				return emoji[keyword]
		return default_emoji

	def __format_selftext(self):
		"""format message based on post type"""

		def format_markdown(text):
			"""apply replacements to markdown for better Discord readability"""

			def format_headings(text):
				"""substitute headings like `### title` with TITLE"""

				def transform_title(match):
					"""transform matched group to uppercase"""
					return match.group(1).upper()

				return re.sub(r"(?:^|(?<=\n))#+[ \t]*(.*?\n)", transform_title, text)

			return format_headings(text)

		def trim_text(text, limit=600):
			"""trim text if over limit of characters"""
			if len(text) > limit:
				# trim text if over limit of characters
				return text[:limit] + "..."
			# otherwise, return original
			return text

		def format_announcements_post(post):
			"""display only theme and schedule in announcements"""
			selftext = ""
			# extract theme from post text
			themeMatch = re.findall(r"(The theme .*?: .*?)\n", post.selftext)
			if len(themeMatch) > 0:
				selftext += themeMatch[0]
			puzzlesMatch = re.findall(
				r"(Puzzle \d)\|(\[.*?\]\(.*?\))\|(\[.*?\]\(.*?\))\|", post.selftext
			)
			for puzzle in puzzlesMatch:
				selftext += f"\n\n**{puzzle[0]}**\n{puzzle[1]} until {puzzle[2]}"
			return selftext

		def format_results_post(post):
			"""tabulate points in results post and trim"""
			selftext = post.selftext
			# find points in post text
			pointsMatch = re.findall(
				r"(?:Puzzle"
				r" (\d+)|.*?Points)\|\**(\d+?)\**\|\**(\d+?)\**\|\**(\d+?)\**\|\**(\d+?)\**\|",
				post.selftext,
			)
			# create table header
			table = [
				"+-----+-----+-----+-----+-----+",
				"|  #  |  G  |  H  |  R  |  S  |",
				"+=====+=====+=====+=====+=====+",
			]
			# add table body
			for p in pointsMatch:
				# number for puzzles, "+" for total row
				num = f" {p[0]} " if len(p[0]) > 0 else "SUM"
				# double row for row before totals
				divider = (
					"+-----+-----+-----+-----+-----+"
					if p != pointsMatch[-2]
					else "+=====+=====+=====+=====+=====+"
				)
				# add table row
				table += [
					f"| {num} |{p[1].rjust(4)} |{p[2].rjust(4)} |{p[3].rjust(4)}"
					f" |{p[4].rjust(4)} |",
					divider,
				]
			# replace markdown table
			selftext = re.sub(
				r"\*\*Level\*\*\|(?:.|\n)*? Points\|.*\n",
				"```\n" + "\n".join(table) + "\n```",
				selftext,
			)
			selftext = re.sub("# Current Points ", "\n# Current Points ", selftext)
			# trim text if over limit of characters
			trimLength = max(600, selftext.find("Level Results"))
			selftext = trim_text(selftext, trimLength)
			return format_markdown(selftext)

		def format_puzzle_post(post):
			"""trim puzzle post"""
			# trim text if over limit of characters
			selftext = trim_text(post.selftext)
			return format_markdown(selftext)

		# format text
		default_formatter = format_puzzle_post
		formatters = {
			"announcements": format_announcements_post,
			"results": format_results_post,
		}
		for keyword in formatters.keys():
			if keyword in str(self.post.title).lower():
				return formatters[keyword](self.post)
		return default_formatter(self.post)

	def __build_message(self):
		"""build message from post"""
		# get url and selftext
		emoji = self.__get_emoji()
		title = self.post.title
		url = f"https://www.reddit.com/r/{self.post.subreddit}/comments/{self.post.id}"
		selftext = self.__format_selftext()
		# create the message
		title = f"{emoji}  |  **{title}**"
		message = f"{url}\n\n{selftext}"
		return title, message