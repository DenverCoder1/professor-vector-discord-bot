from discord.ext import commands
from modules.solved.prefix import Prefix


class SolvedCog(commands.Cog):
	"""Checks for `solved` and `unsolved` command
	Toggles `solved-` prefix on channel name"""

	def __init__(self, bot):
		self.bot = bot
		self.prefix = "solved"

	@commands.command(name="solved")
	async def solved(self, ctx):
		"""Changes channel name to solved-<channel-name>"""
		# log command in console
		print("Received solved command")
		# get channel
		channel = ctx.message.channel
		# create prefix checking object
		p = Prefix(channel, self.prefix)
		# check if already solved
		if not p.has_prefix():
			new_channel_name = p.add_prefix()
			# reply to user
			await ctx.send(f"Marking {channel} as solved!")
			# rename channel to append prefix
			await channel.edit(name=new_channel_name)
		# already solved
		else:
			# reply to user
			await ctx.send(f"Channel already marked as solved!")

	@commands.command(name="unsolved")
	async def unsolved(self, ctx):
		"""removed solved prefix from channel name"""
		# log command in console
		print("Received unsolved command")
		# get channel
		channel = ctx.message.channel
		# create prefix checking object
		p = Prefix(channel, self.prefix)
		# check if already solved
		if p.has_prefix():
			# edit channel name to remove prefix
			new_channel_name = p.remove_prefix()
			# reply to user
			await ctx.send(f"Marking {new_channel_name} as unsolved!")
			# rename channel to remove prefix
			await channel.edit(name=new_channel_name)
		# already solved
		else:
			# reply to user
			await ctx.send(f"Channel is not solved!")


def setup(bot):
	bot.add_cog(SolvedCog(bot))
