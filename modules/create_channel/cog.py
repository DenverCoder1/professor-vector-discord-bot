import os
from dotenv.main import load_dotenv
from discord.ext import commands

load_dotenv()

# Test Server
DISCORD_GUILD = int(os.getenv("DISCORD_GUILD"))


class CreateChannelCog(commands.Cog):
	"""Checks for `resend` command and starts Reddit feed loop to check submissions"""

	def __init__(self, bot):
		self.bot = bot

	def is_in_guild(guild_id):
		"""check that command is in a guild"""

		async def predicate(ctx):
			return ctx.guild and ctx.guild.id == guild_id

		return commands.check(predicate)

	@commands.command(name="createchannel")
	@is_in_guild(DISCORD_GUILD)
	async def createchannel(self, ctx, arg=None):
		"""Command to create channel in same category with given name"""
		# log command in console
		print("Received createchannel command")
		# respond to command
		if arg != None:
			guild = ctx.message.guild
			category = ctx.channel.category
			await ctx.send(f"Creating channel {arg} in {category}!")
			# create channel
			await guild.create_text_channel(arg, category=category)
		# no argument passed
		else:
			await ctx.send(f"You must specify a channel name!")


def setup(bot):
	bot.add_cog(CreateChannelCog(bot))
