import os
from dotenv.main import load_dotenv
import discord
from discord.ext import commands

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BOT_PREFIX = "!"

def main():
	# allows privledged intents for monitoring members joining, roles editing, and role assignments
    # these need to be enabled in the developer portal as well
	intents = discord.Intents.default()
	intents.guilds = True
	intents.members = True

	client = commands.Bot(BOT_PREFIX, intents=intents)  # bot command prefix

	# Get the modules of all cogs whose directory structure is modules/<module_name>/cog.py
	for folder in os.listdir("modules"):
		if os.path.exists(os.path.join("modules", folder, "cog.py")):
			client.load_extension(f"modules.{folder}.cog")

	@client.event
	async def on_ready():
		"""When discord is connected"""
		print(f"{client.user.name} has connected to Discord!")

	# Run Discord bot
	client.run(DISCORD_TOKEN)


if __name__ == "__main__":
	main()
