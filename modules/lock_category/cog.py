from nextcord.ext import commands
import nextcord


class LockCategoryCog(commands.Cog, name="Lock Category"):
	"""Checks for `lockcategory` command
	Lock `@everyone` from writing in a given category"""

	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="lockcategory")
	@commands.has_permissions(administrator=True)
	async def lockcategory(self, ctx, *args):
		"""Command to lock `@everyone` from writing in a given category"""
		# log command in console
		print("Received lockcategory command")
		# check if category specified
		if len(args) > 0:
			# join arguments to form channel name
			category_name = " ".join(args)
			# get new category
			category = nextcord.utils.get(ctx.guild.channels, name=category_name)
			if category is not None:
				# lock category
				await category.set_permissions(
					ctx.guild.default_role, send_messages=False
				)
				# reply to user
				await ctx.send(f"Locked {category}!")
			else:
				# reply to user
				await ctx.send(f"Could not find category `{category_name}`")
		# no argument passed
		else:
			# reply to user
			await ctx.send(f"You must specify a category!")


def setup(bot):
	bot.add_cog(LockCategoryCog(bot))
