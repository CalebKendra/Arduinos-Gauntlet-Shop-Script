from pathlib import Path
import random
import textwrap

import pandas as pd
from rich.console import Console
from rich.table import Table


CONSOLE = Console()



# Change this from 1 to 10 to bias the shop toward weaker or stronger items.
CHARACTER_LEVEL = 2

# Set to True to show target ItemValue and per-row ItemValue numbers.
DEBUG_MODE = True

# Exponential scaling for target ItemValue growth by level.
# 1.0 = linear, >1.0 grows slower early and faster later, <1.0 does the opposite.
# Means the target ItemValue at level 10 will be 100.0, and at level 1 will be 0.0, with the curve shape determined by the exponent.
TARGET_VALUE_SCALING_EXPONENT = 1.6

# Controls how wide the offered ItemValue band is around the level target.
# Example: 15 means roughly target +/- 15 ItemValue.
BIG_SIX_ITEMVALUE_RANGE_WIDTH = 2.0
POTIONS_AND_SCROLLS_ITEMVALUE_RANGE_WIDTH = 5.0
UNIQUES_ITEMVALUE_RANGE_WIDTH = 5.0

# Additional width added per level above 1.
# Example: 1.0 means level 10 adds +9 width.
BIG_SIX_ITEMVALUE_RANGE_GROWTH_PER_LEVEL = 1.0
POTIONS_AND_SCROLLS_ITEMVALUE_RANGE_GROWTH_PER_LEVEL = 1.0
UNIQUES_ITEMVALUE_RANGE_GROWTH_PER_LEVEL = 1.0

# Number of items to show per shop section.
BIG_SIX_ITEMS_PER_SECTION = 3
POTIONS_AND_SCROLLS_ITEMS_PER_SECTION = 3
UNIQUES_ITEMS_PER_SECTION = 5

# Change these values to adjust token pricing per CSV.
BIG_SIX_TOKEN_SCALE = 3.0
POTIONS_AND_SCROLLS_TOKEN_SCALE = 1.0
UNIQUES_TOKEN_SCALE = 1.0

# Lower than 1.0 makes scrolls less likely to be selected in Potions and Scrolls.
# Example: 0.5 means scrolls get half the normal selection weight.
POTIONS_AND_SCROLLS_SCROLL_WEIGHT_MULTIPLIER = 0.1

CSV_CONFIGS = [
	{
		"path": Path("big_six.csv"),
		"label": "Big Six",
		"token_scale": BIG_SIX_TOKEN_SCALE,
		"items_per_section": BIG_SIX_ITEMS_PER_SECTION,
		"range_width": BIG_SIX_ITEMVALUE_RANGE_WIDTH,
		"range_growth_per_level": BIG_SIX_ITEMVALUE_RANGE_GROWTH_PER_LEVEL,
	},
	{
		"path": Path("potions_and_scrolls.csv"),
		"label": "Potions and Scrolls",
		"token_scale": POTIONS_AND_SCROLLS_TOKEN_SCALE,
		"scroll_weight_multiplier": POTIONS_AND_SCROLLS_SCROLL_WEIGHT_MULTIPLIER,
		"items_per_section": POTIONS_AND_SCROLLS_ITEMS_PER_SECTION,
		"range_width": POTIONS_AND_SCROLLS_ITEMVALUE_RANGE_WIDTH,
		"range_growth_per_level": POTIONS_AND_SCROLLS_ITEMVALUE_RANGE_GROWTH_PER_LEVEL,
	},
	{
		"path": Path("uniques.csv"),
		"label": "Uniques",
		"token_scale": UNIQUES_TOKEN_SCALE,
		"items_per_section": UNIQUES_ITEMS_PER_SECTION,
		"range_width": UNIQUES_ITEMVALUE_RANGE_WIDTH,
		"range_growth_per_level": UNIQUES_ITEMVALUE_RANGE_GROWTH_PER_LEVEL,
	},
]


def level_to_target_value(level: int) -> float:
	level = max(1, min(10, int(level)))
	normalized_level = (level - 1) / 9
	exponent = max(0.01, float(TARGET_VALUE_SCALING_EXPONENT))
	return (normalized_level**exponent) * 100.0


def level_to_range_width(level: int, base_width: float, growth_per_level: float) -> float:
	level = max(1, min(10, int(level)))
	return max(0.0, float(base_width) + ((level - 1) * float(growth_per_level)))


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
	scroll_weight_multiplier: float = 1.0,
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

		if "Group" in remaining.columns:
			group_lower = remaining["Group"].fillna("").astype(str).str.lower().str.strip()
			scroll_mask = group_lower == "scroll"
		elif "Name" in remaining.columns:
			name_lower = remaining["Name"].fillna("").astype(str).str.lower().str.strip()
			scroll_mask = name_lower.str.startswith("scroll of ")
		else:
			scroll_mask = pd.Series(False, index=remaining.index)

		if scroll_mask.any():
			weights = weights.where(~scroll_mask, weights * max(0.0, float(scroll_weight_multiplier)))

		if float(weights.sum()) <= 0.0:
			weights = pd.Series([1.0] * len(remaining), index=remaining.index)

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
	CONSOLE.print(f"\n[bold cyan]{label}[/bold cyan]")
	if items.empty:
		CONSOLE.print("[yellow]No items available.[/yellow]")
		return

	table = Table(show_header=True, header_style="bold", expand=False, show_lines=True)
	table.add_column("Name", width=34)
	if debug_mode:
		table.add_column("ItemValue", justify="right", width=10)
	table.add_column("Tokens", justify="right", width=8)
	table.add_column("Description", width=54)

	for number, (_, row) in enumerate(items.iterrows(), start=1):
		name = clean_description(row.get("Name", ""))
		description = clean_description(row.get("Description", ""))
		item_value = float(pd.to_numeric(row.get("ItemValue"), errors="coerce"))
		tokens = token_cost_for_item(item_value, token_scale)
		name_text = "\n".join(wrap_cell(name, 34))
		description_text = "\n".join(wrap_cell(description, 54, max_lines=3))

		if debug_mode:
			table.add_row(
				name_text,
				f"{item_value:.2f}",
				str(tokens),
				description_text,
			)
		else:
			table.add_row(
				name_text,
				str(tokens),
				description_text,
			)

	CONSOLE.print(table)


def main() -> None:
	target_value = level_to_target_value(CHARACTER_LEVEL)
	print(f"Character level: {CHARACTER_LEVEL}")
	if DEBUG_MODE:
		print(f"Target ItemValue: {target_value:.2f}")
		print("\nItemValue range width settings:")
		for config in CSV_CONFIGS:
			range_width = level_to_range_width(
				CHARACTER_LEVEL,
				config["range_width"],
				config["range_growth_per_level"],
			)
			print(
				f"- [{config['label']}] +/-{range_width:.2f} "
				f"(base {config['range_width']}, growth {config['range_growth_per_level']})"
			)

	for config in CSV_CONFIGS:
		range_width = level_to_range_width(
			CHARACTER_LEVEL,
			config["range_width"],
			config["range_growth_per_level"],
		)

		if not config["path"].exists():
			print(f"\n== {config['label']} ==")
			print(f"Missing file: {config['path']}")
			continue

		frame = pd.read_csv(config["path"])
		if "ItemValue" not in frame.columns:
			print(f"\n== {config['label']} ==")
			print("ItemValue column not found.")
			continue

		items = weighted_sample(
			frame,
			target_value,
			range_width=range_width,
			scroll_weight_multiplier=config.get("scroll_weight_multiplier", 1.0),
			count=config["items_per_section"],
		)
		print_shop_section(
			config["label"],
			items,
			config["token_scale"],
			DEBUG_MODE,
		)


if __name__ == "__main__":
	main()