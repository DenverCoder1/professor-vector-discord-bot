class Prefix:
	def __init__(self, original: str, prefix: str):
		self.original = str(original)
		self.prefix = str(prefix)
		self.prefix_len = len(self.prefix)

	def has_prefix(self):
		return self.original[: self.prefix_len] == self.prefix

	def add_prefix(self):
		return f"{self.prefix}-{self.original}"

	def remove_prefix(self):
		return self.original[self.prefix_len + 1 :]
