import config
import discord
from discord.ext import commands

class MoveChannelCog(commands.Cog, name="Move Channel"):
	"""Checks for `movechannel` command
	Moves current channel to given category"""

	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="movechannel")
	@commands.has_any_role(
		config.MYSTERY_HUNT_ROLE_ID,
		config.VERIFIED_PUZZLER_ROLE_ID,
		config.TEST_HUNTER_ROLE_ID,
	)
	async def movechannel(self, ctx, *args):
		"""Command to move channel to category with given name"""
		# log command in console
		print("Received movechannel command")
		# check for category name arguments
		if len(args) > 0:
			# join arguments to form channel name
			category_name = " ".join(args)
			# get current channel
			channel = ctx.channel
			# get new category
			new_category = discord.utils.get(ctx.guild.channels, name=category_name)
			if new_category is not None:
				# reply to user
				await ctx.send(f"Moving {channel.mention} to {new_category}!")
				# move channel
				await ctx.channel.edit(category=new_category)
			else:
				# reply to user
				await ctx.send(f"Could not find category `{category_name}`")
		# no argument passed
		else:
			# reply to user
			await ctx.send(f"You must specify a category!")


def setup(bot):
	bot.add_cog(MoveChannelCog(bot))
