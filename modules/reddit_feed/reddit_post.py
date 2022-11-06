import datetime
import re
from typing import Optional

import config
import nextcord
from table2ascii import Alignment, table2ascii
from utils.embedder import build_embed


class RedditPost:
	def __init__(self, bot, post):
		self.bot = bot
		self.post = post
		self.post_url = f"https://redd.it/{post.id}"

	async def process_post(self, message_id: Optional[int] = None):
		"""check post and announce if not saved"""
		# log post details in console
		print(f"Recieved post by {self.post.author} at {self.__get_date()}")
		# create message with url and text
		title, message = self.__build_message()
		if not message_id:
			# send to discord announcements
			await self.__announce(title, message)
			# log announcement status in console
			print(f"Sent announcement.")
		else:
			# edit announcement
			await self.__edit_announcement(title, message, message_id)
			# log announcement status in console
			print(f"Edited announcement.")

	async def __announce(self, title: str, description: str):
		"""send message in announcements channel"""
		channel: nextcord.TextChannel = self.bot.get_channel(config.ANNOUNCEMENTS_CHANNEL_ID)
		embed = build_embed(title, description, url=self.post_url)
		message: nextcord.Message = await channel.send(embed=embed)
		try:
			await message.publish()
		except Exception:
			pass

	async def __edit_announcement(self, title: str, description: str, message_id: int):
		"""edit message in announcements channel"""
		channel: nextcord.TextChannel = self.bot.get_channel(config.ANNOUNCEMENTS_CHANNEL_ID)
		message: nextcord.Message = await channel.fetch_message(message_id)
		embed = build_embed(title, description, url=self.post_url)
		await message.edit(embed=embed)

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

				return re.sub(r"(?:^|(?<=[\n\r]))#+[ \t]*([^\n\r]*[\n\r])", transform_title, text)

			def format_spoilers(text):
				"""substitute spoilers like `>!spoiler!<` with `||spoiler||`"""
				return re.sub(r">!((?:.|\s)*?)(?:!<|$)", r"||\1||", text)

			return format_spoilers(format_headings(text))

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
			theme_match = re.findall(r"(The theme .*?: .*?)\n", post.selftext)
			if len(theme_match) > 0:
				selftext += theme_match[0]
			puzzles_match = re.findall(
				r"([^|]*?)\|([^|]*?\d, [^|]*?)\|([^|]*?\d, [^|]*?)\|",
				post.selftext,
			)
			for puzzle in puzzles_match:
				selftext += f"\n**{puzzle[0]}**\n{puzzle[1]} until {puzzle[2]}"
			return selftext

		def format_results_post(post):
			"""tabulate points in results post and trim"""
			selftext = post.selftext
			# find points in post text
			points_match = re.findall(
				r"\w.*?(\d*)\|\**(\d+?)\**\|\**(\d+?)\**\|\**(\d+?)\**\|\**(\d+?)\**\|",
				post.selftext,
			)
			if points_match:
				# create unicode table
				table = table2ascii(
					header=["#", "G", "H", "R", "S"],
					body=points_match[0:-1],
					footer=["SUM"] + list(points_match[-1][1:]),
					first_col_heading=True,
					alignments=[Alignment.CENTER] + [Alignment.RIGHT] * 4,
				)
				# replace markdown table
				selftext = re.sub(
					r"\*\*Level\*\*\|(?:.|\n)*? Points\|.*\n+",
					"```ml\n" + table + "\n```\n",
					selftext,
				)
				selftext = re.sub("# Current Points ", "\n# Current Points ", selftext)
			# trim text if over limit of characters
			trim_length = max(600, selftext.find("Level Results"))
			selftext = trim_text(selftext, trim_length)
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
		selftext = self.__format_selftext()
		# create the message
		title = f"{emoji}  |  **{title}**"
		message = f"{self.post_url}\n\n{selftext}"
		return title, message
