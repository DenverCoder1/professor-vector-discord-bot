import nextcord
import os
from nextcord.ext import commands
import config


def main():
	# allows privledged intents for monitoring members joining, roles editing, and role assignments
	# these need to be enabled in the developer portal as well
	intents = nextcord.Intents.default()
	intents.guilds = True
	intents.members = True

	client = commands.Bot(config.BOT_PREFIX, intents=intents)

	# Get the modules of all cogs whose directory structure is modules/<module_name>/cog.py
	for folder in os.listdir("modules"):
		if os.path.exists(os.path.join("modules", folder, "cog.py")):
			client.load_extension(f"modules.{folder}.cog")

	@client.event
	async def on_ready():
		"""When discord is connected"""
		print(f"{client.user.name} has connected to Discord!")

	# Run Discord bot
	client.run(config.DISCORD_TOKEN)


if __name__ == "__main__":
	main()
