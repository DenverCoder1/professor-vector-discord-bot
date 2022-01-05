from dotenv.main import load_dotenv
import os

load_dotenv()

# Discord config
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BOT_PREFIX = "!"

# Reddit config
ME = os.getenv("REDDIT_USERNAME")
PASSWORD = os.getenv("REDDIT_PASSWORD")
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
SUB = os.getenv("REDDIT_SUB", "Arithmancy")

# Guild
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))

# Announcements channel
ANNOUNCEMENTS_CHANNEL_ID = int(os.getenv("DISCORD_ANNOUNCEMENTS_CHANNEL"))

# Roles
MYSTERY_HUNT_ROLE_ID = 788526627440689242 # Arithmancy
VERIFIED_PUZZLER_ROLE_ID = 812906479794520135 # Team Arithmancy
TEST_HUNTER_ROLE_ID = 798768131849977856 # Test (Eyl)