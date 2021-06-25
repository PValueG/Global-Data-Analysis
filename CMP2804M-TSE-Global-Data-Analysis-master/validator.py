from collections import namedtuple
from json import load
from re import search, match
from time import time

from pandas import read_csv
from pandas import DataFrame

YEAR_MATCHES = ("year", "time", "yr")
COUNTRY_MATCHES = ("country", "alpha", "iso", "m49", "name")

Country = namedtuple("Country", ["name", "a2", "a3", "m49"])

with open("./assets/countries.json", encoding="utf-8") as file:
	country_data = load(file)


class Validator(object):
	def __init__(self, dfs, lang="gb"):
		if not isinstance(dfs, list) and not isinstance(dfs, tuple):
			raise TypeError("`Validator` takes a list or tuple of DataFrame objects.")

		for df in dfs:
			if not isinstance(df, DataFrame):
				raise TypeError("`Validator` takes a list or tuple of DataFrame objects.")
		
		self.dfs = dfs

		if lang not in ("gb", "us"):
			raise ValueError("`lang` parameter needs to be either 'gb' or 'us'.")

		self.lang = lang
		self.latest = 0

	def tokenise_columns(self):
		punc = "!\"#&'()*+,./:;<=>?@[\\]^_`{|}~"
		max_cols = 0
		tokens = []
		translations = load(open(f"./assets/{'us-gb' if self.lang == 'gb' else 'gb-us'}.json", "r"))

		def translate(column):
			column = column.split(" ")
			col = ""
			spl = []

			for idx, word in enumerate(column):
				p = ""

				for char in word:
					if char in punc:
						p += char
						word = word.replace(char, "")

				if word.lower() in translations.keys():
					if idx == 0:
						word = translations[word.lower()].title()

					else:
						word = translations[word]

				try:
					word = f"{int(word):,}"
					p = p.replace(",", "")
					# spl.append(f"{int(word):,}")
					# col += f"{int(word):,} "

				except ValueError:
					pass

				spl.append(word)

				if len(p) > 0 and p[0] == "(":
					col += f"{p[0]}{word}{p[1:]} "

				else:
					col += f"{word}{p} "

			return col.strip()

		def split(phrase):
			for char in punc:
				phrase = phrase.replace(char, "")

			return phrase.split(" ")

		def tokenise(column):
			# print(column)
			column = translate(column)
			# print(column)
			item = {
				"raw": [column],
				"tokens": [],
				"combos": [],
				"context": None,
				"unit": None,
			}

			if (match := search(r'\(.*\)', column)) is not None:
				# print(column)
				# print(match)
				item["unit"] = match.group()[1:-1]
				column = column[:match.span()[0]-1]

			if len(column.split(",")) > 1:
				item["context"] = (ctx := column.split(",")[-1].strip())
				column = column.replace(f", {ctx}", "")

			for idx, word in enumerate((spl := split(column))): # split has to be done twice
				if word in ("and", "of"):
					item["combos"].append(f"{spl[idx-1]} {spl[idx]} {spl[idx+1]}")

				else:
					item["tokens"].append(word)

			return item

		for df in self.dfs:
			if len(df.columns) > max_cols:
				max_cols = len(df.columns)

			for column in df.columns:
				tokens.append(tokenise(column))

		# for item in tokens:
		# 	for key, value in item.items():
		# 		print(f"{key}: {value}")

		# 	print()

		# 	print()

	def build_collated_df(self):
		punc = "!\"#&'()*+,-./:;<=>?@[\\]^_`{|}~"
		col_tokens = []
		df_cols = []

		for df in self.dfs:
			if len(df.columns) > len(df_cols):
				df_cols = list(df.columns)

			for column in df.columns:
				for char in punc:
					column = column.replace(char, "")

				col_tokens.append((df, column.split(" ")))

		# for ct in col_tokens:
		# 	print(ct[1])

		#XX test stuff + beta. Not run in alpha
		# self.tokenise_columns()
		# quit()

		self.country_column = next((c for c in df_cols if any([kw in c.lower().split(" ") for kw in COUNTRY_MATCHES])))
		self.year_column = next((c for c in df_cols if any([kw in c.lower().split(" ") for kw in YEAR_MATCHES])))

		cols = ["Dataset Index", "Data Year"]
		extras = len(cols)
		cols.extend(df_cols)
		data = {col: [] for col in cols}
		most = 0

		def determine_year(cols, row):
			if (result := search(r'[0-9]{4}', row[1][self.year_column])) is not None:
				return result.group()

		for idx, df in enumerate(self.dfs):
			for row in df.iterrows():
				data["Dataset Index"].append(idx)
				data["Data Year"].append(determine_year(cols, row))

				for idx2, col in enumerate(cols):
					if idx2 >= extras:
						try:
							data[col].append(row[1][idx2-extras])

						except IndexError:
							pass		

		return DataFrame(data, columns=cols)

	def validate(self):
		start = time()

		# build a collated df using data from all datasets
		cdf = self.build_collated_df()

		# do all the validation here
		cdf = self.unify_locations(cdf)

		# output
		print(f"\nValidation took {time()-start:,.3f} secs.")

		# test stuff
		# print(cdf.columns)

		return cdf

	def unify_locations(self, df):
		to_replace = []
		value = []

		def identify(stored):
			"""Checks if `stored` is valid.
			Returns what the country should be for unification.:
			Key: name (preceding)."""

			for c in country_data:
				if stored.lower() == c["country"].lower():
					return stored

				#XX might be changed to include `.lower()` at some point
				elif stored in (c["a2"], c["a3"], c["m49"]):
					return c["country"]

				elif (has_pre := "preceding" in c.keys()):
					if stored.lower() == f"{c['country']} ({c['preceding']})":
						return stored

					elif stored.lower() == f"{c['preceding']} {c['country']}":
						return f"{c['country']} ({c['preceding']})"

				elif "aka" in c.keys() and stored.lower() in c["aka"]:
					return f"{c['country']} ({c['preceding']})" if has_pre else c["country"]

			return "[invalid]"

		def title(phrase):
			parts = []

			for word in phrase.split(" "):
				if word not in ("and", "of"):
					parts.append(word.title())

				else:
					parts.append(word)

			return " ".join(parts)

		for idx, row in enumerate(df.iterrows()):
			stored = row[1][self.country_column]

			if (ret := identify(stored)) == "[invalid]":
				df.drop(index=idx, inplace=True)

			elif ret != stored:
				to_replace.append(stored)
				value.append(ret)

		df[self.country_column].replace(to_replace, value, inplace=True)
		return df


# column tokeniser stuff
# add un countries if they're not there

if __name__ == "__main__":
	# from glob import glob

	# dfs = []

	# for path in glob("./datasets/*.csv"):
	# 	dfs.append(read_csv(path))

	validator = Validator([read_csv("./datasets/worldBank2017.csv")])
	df = validator.validate()