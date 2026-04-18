from pathlib import Path
import random
import textwrap

import pandas as pd


# Change this from 1 to 10 to bias the shop toward weaker or stronger items.
CHARACTER_LEVEL = 10

# Controls how wide the offered ItemValue band is around the level target.
# Example: 15 means roughly target +/- 15 ItemValue.
ITEMVALUE_RANGE_WIDTH = 8.0
# Additional width added per level above 1.
# Example: 1.0 means level 10 adds +9 width.
ITEMVALUE_RANGE_GROWTH_PER_LEVEL = 1.0

# Set to True to show target ItemValue and per-row ItemValue numbers.
DEBUG_MODE = True

# Change these values to adjust token pricing per CSV.
BIG_SIX_TOKEN_SCALE = 1.0
POTIONS_AND_SCROLLS_TOKEN_SCALE = 1.0
UNIQUES_TOKEN_SCALE = 1.0

CSV_CONFIGS = [
	{
		"path": Path("big_six.csv"),
		"label": "Big Six",
		"token_scale": BIG_SIX_TOKEN_SCALE,
	},
	{
		"path": Path("potions_and_scrolls.csv"),
		"label": "Potions and Scrolls",
		"token_scale": POTIONS_AND_SCROLLS_TOKEN_SCALE,
	},
	{
		"path": Path("uniques.csv"),
		"label": "Uniques",
		"token_scale": UNIQUES_TOKEN_SCALE,
	},
]


def level_to_target_value(level: int) -> float:
	level = max(1, min(10, int(level)))
	return ((level - 1) / 9) * 100.0


def level_to_range_width(level: int) -> float:
	level = max(1, min(10, int(level)))
	return max(0.0, ITEMVALUE_RANGE_WIDTH + ((level - 1) * ITEMVALUE_RANGE_GROWTH_PER_LEVEL))


def clean_description(value) -> str:
	if pd.isna(value):
		return ""
	text = str(value).strip()
	if text.lower() == "nan":
		return ""
	return text


def wrap_cell(text: str, width: int, max_lines: int | None = None) -> list[str]:
	cleaned = clean_description(text)
	if not cleaned:
		return [""]
	lines = textwrap.wrap(cleaned, width=width) or [""]
	if max_lines is not None and len(lines) > max_lines:
		lines = lines[:max_lines]
		if lines[-1]:
			lines[-1] = lines[-1].rstrip() + "..."
		else:
			lines[-1] = "..."
	return lines


def token_cost_for_item(item_value: float, token_scale: float) -> int:
	normalized_value = max(0.0, min(1.0, float(item_value) / 100.0))
	raw_cost = 1 + (normalized_value * 9 * token_scale)
	return max(1, min(10, int(round(raw_cost))))


def weighted_sample(
	frame: pd.DataFrame,
	target_value: float,
	range_width: float,
	count: int = 3,
) -> pd.DataFrame:
	pool = frame.copy()
	pool["ItemValue"] = pd.to_numeric(pool["ItemValue"], errors="coerce")
	pool = pool.dropna(subset=["ItemValue"])
	if pool.empty:
		return pool

	min_value = max(0.0, target_value - range_width)
	max_value = min(100.0, target_value + range_width)
	range_pool = pool[(pool["ItemValue"] >= min_value) & (pool["ItemValue"] <= max_value)]

	# If the band is too narrow, fall back to full pool so we can still return items.
	if len(range_pool) >= count:
		pool = range_pool

	selected_rows = []
	remaining = pool.copy()
	for _ in range(min(count, len(remaining))):
		distances = (remaining["ItemValue"] - target_value).abs()
		weights = 1 / (1 + distances)
		chosen_index = random.choices(
			population=list(remaining.index),
			weights=weights.tolist(),
			k=1,
		)[0]
		selected_rows.append(remaining.loc[chosen_index])
		remaining = remaining.drop(chosen_index)

	return pd.DataFrame(selected_rows)


def print_shop_section(
	label: str,
	items: pd.DataFrame,
	token_scale: float,
	debug_mode: bool,
) -> None:
	print(f"\n== {label} ==")
	if items.empty:
		print("No items available.")
		return

	if debug_mode:
		columns = ["#", "Name", "ItemValue", "Tokens", "Description"]
		widths = [3, 34, 10, 8, 54]
	else:
		columns = ["#", "Name", "Tokens", "Description"]
		widths = [3, 34, 8, 54]
	description_width = widths[-1]
	separator = "+" + "+".join("-" * (width + 2) for width in widths) + "+"

	def format_row(values: list[str]) -> str:
		return "|" + "|".join(f" {value:<{width}} " for value, width in zip(values, widths)) + "|"

	print(separator)
	print(format_row(columns))
	print(separator)

	for number, (_, row) in enumerate(items.iterrows(), start=1):
		name = clean_description(row.get("Name", ""))
		description = clean_description(row.get("Description", ""))
		item_value = float(pd.to_numeric(row.get("ItemValue"), errors="coerce"))
		tokens = token_cost_for_item(item_value, token_scale)
		name_lines = wrap_cell(name, widths[1])
		description_lines = wrap_cell(description, description_width, max_lines=3)
		row_height = max(len(name_lines), len(description_lines))

		for index in range(row_height):
			if debug_mode:
				row_values = [
					str(number) if index == 0 else "",
					name_lines[index] if index < len(name_lines) else "",
					f"{item_value:.2f}" if index == 0 else "",
					str(tokens) if index == 0 else "",
					description_lines[index] if index < len(description_lines) else "",
				]
			else:
				row_values = [
					str(number) if index == 0 else "",
					name_lines[index] if index < len(name_lines) else "",
					str(tokens) if index == 0 else "",
					description_lines[index] if index < len(description_lines) else "",
				]
			print(format_row(row_values))
		print(separator)


def main() -> None:
	target_value = level_to_target_value(CHARACTER_LEVEL)
	range_width = level_to_range_width(CHARACTER_LEVEL)
	print(f"Character level: {CHARACTER_LEVEL}")
	if DEBUG_MODE:
		print(f"Target ItemValue: {target_value:.2f}")
		print(f"ItemValue range width: +/-{range_width:.2f}")

	for config in CSV_CONFIGS:
		if not config["path"].exists():
			print(f"\n== {config['label']} ==")
			print(f"Missing file: {config['path']}")
			continue

		frame = pd.read_csv(config["path"])
		if "ItemValue" not in frame.columns:
			print(f"\n== {config['label']} ==")
			print("ItemValue column not found.")
			continue

		items = weighted_sample(frame, target_value, range_width=range_width, count=3)
		print_shop_section(
			config["label"],
			items,
			config["token_scale"],
			DEBUG_MODE,
		)


if __name__ == "__main__":
	main()