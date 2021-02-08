from .text_to_table import TextToTable

table = TextToTable(
	["#", "G", "H", "R", "S"],
	[["1", "30", "40", "35", "30"], ["2", "30", "40", "35", "30"]],
	["SUM", "130", "140", "135", "130"],
).tableize()

print(table)