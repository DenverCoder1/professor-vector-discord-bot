import traceback
from discord import logging
from discord.ext.commands.errors import *
from datetime import datetime


class ErrorHandler:
	"""
	Handles different types of error messages
	"""

	def __init__(self, message, error, human_details):
		self.message = message
		self.error = error
		self.human_details = human_details
		# formats the error as traceback
		self.trace = traceback.format_exc()

	async def handle_error(self):
		"""When an exception is raised, log it in err.log and bot log channel"""
		error_details = self.trace if self.trace != "NoneType: None\n" else self.error
		# logs error as warning in console
		logging.warning(error_details)
		# log to err.log
		self.__log_to_file("err.log", error_details)
		# notify user of error
		user_error = self.__user_error_message()
		if user_error:
			await self.message.channel.send(user_error)

	def __user_error_message(self):
		if isinstance(self.error, CommandNotFound):
			pass  # ignore command not found
		elif isinstance(self.error, MissingRequiredArgument):
			return f"Argument {self.error.param} required."
		elif isinstance(self.error, TooManyArguments):
			return f"Too many arguments given."
		elif isinstance(self.error, BadArgument):
			return f"Bad argument: {self.error}"
		elif isinstance(self.error, NoPrivateMessage):
			return f"That command cannot be used in DMs."
		elif isinstance(self.error, MissingPermissions):
			return (
				"You are missing the following permissions required to run the"
				f' command: {", ".join(self.error.missing_perms)}.'
			)
		elif isinstance(self.error, DisabledCommand):
			return f"That command is disabled or under maintenance."
		elif isinstance(self.error, CommandInvokeError):
			return f"Error while executing the command."
		elif "Role" in str(self.error) and "is required" in str(self.error):
			return self.error

	def __log_to_file(self, filename: str, text: str):
		"""appends the date and logs text to a file"""
		with open(filename, "a", encoding="utf-8") as f:
			# write the current time and log text at end of file
			f.write(f"{datetime.now()}\n{text}\n------------------------------------\n")
