import config
from discord.ext import commands


class CreateChannelCog(commands.Cog, name="Create Channel"):
	"""Checks for `createchannel` command
	Creates channel in same category with given name"""

	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="createchannel")
	@commands.has_any_role(
		config.MYSTERY_HUNT_ROLE_ID,
		config.VERIFIED_PUZZLER_ROLE_ID,
		config.TEST_HUNTER_ROLE_ID,
	)
	async def createchannel(self, ctx, name: str = ""):
		"""Command to create channel in same category with given name"""
		# log command in console
		print("Received createchannel command")
		# check for channel name argument
		if len(name) > 0:
			# get guild and category
			guild = ctx.message.guild
			category = ctx.channel.category
			# create channel
			channel = await guild.create_text_channel(name, category=category)
			# reply to user
			await ctx.send(f"Created channel {channel.mention} in {category}!")
		# no argument passed
		else:
			# reply to user
			await ctx.send(f"You must specify a channel name!")


def setup(bot):
	bot.add_cog(CreateChannelCog(bot))
