from pathlib import Path
import random
import textwrap

import pandas as pd
from rich.console import Console
from rich.table import Table


CONSOLE = Console()


# Change this from 1 to 10 to bias the shop toward weaker or stronger items.
CHARACTER_LEVEL = 3

# Set to True to show target ItemValue and per-row ItemValue numbers.
DEBUG_MODE = True

#
# TARGET VALUE SCALING SETTINGS
#

# Determines the rate at which target ItemValue increasingly grows by level.
# Linear means the target ItemValue at level 10 will be 100.0, and at level 1 will be 0.0, with the curve shape determined by the exponent.
# 1.0 = linear, >1.0 grows slower early and faster later, <1.0 does the opposite.
TARGET_VALUE_SCALING_EXPONENT = 3.0

#
# ITEMVALUE RANGE SETTINGS
#

# Controls how wide the offered ItemValue band is around the level target.
# Example: 15 means roughly target +/- 15 ItemValue.
BIG_SIX_ITEMVALUE_RANGE_WIDTH = 2.0
POTIONS_AND_SCROLLS_ITEMVALUE_RANGE_WIDTH = 5.0
UNIQUES_ITEMVALUE_RANGE_WIDTH = 2.0

# Additional width added per level above 1.
# Example: 1.0 means level 10 adds +9 width.
BIG_SIX_ITEMVALUE_RANGE_GROWTH_PER_LEVEL = 0.5
POTIONS_AND_SCROLLS_ITEMVALUE_RANGE_GROWTH_PER_LEVEL = 1.0
UNIQUES_ITEMVALUE_RANGE_GROWTH_PER_LEVEL = 0.75

#
# ITEMS PER SECTION SETTINGS
#

# Number of items to show per shop section.
BIG_SIX_ITEMS_PER_SECTION = 2
POTIONS_AND_SCROLLS_ITEMS_PER_SECTION = 4
UNIQUES_ITEMS_PER_SECTION = 4

#
# GROUP TOKEN COST SETTINGS
#

# Per-CSV token modifiers applied to every item in that CSV.
# 1.0 = no change, 1.2 = 20% more expensive, 0.8 = 20% cheaper.
BIG_SIX_TOKEN_CSV_MODIFIER = 1.5
POTIONS_AND_SCROLLS_TOKEN_CSV_MODIFIER = 0.4
UNIQUES_TOKEN_CSV_MODIFIER = 1.6


# Specific item group token cost modifiers.
# JSON-style token modifiers applied after the base relative price is calculated.
# Keys are checked as substrings against the item group, and matching entries multiply the final token cost.
BIG_SIX_TOKEN_SPECIAL_MODIFIERS = {
	'Wondrous Item': 1.3,
	'Ring': 1.3,
	'Weapon Upgrade': 1.15,
	'Armor Upgrade': 1.15,
}
POTIONS_AND_SCROLLS_TOKEN_SPECIAL_MODIFIERS = {
}
UNIQUES_TOKEN_SPECIAL_MODIFIERS = {
}

#
# TOKEN COST COMPARED TO ITEMVALUE SETTINGS
#

# Items near the TOKEN_BASE_COST_AT_TARGET variable have this token cost amount before modifiers.
TOKEN_BASE_COST_AT_TARGET = 4.0
# Cost shift applied per 1x range width above target.
# Higher values make items above target ramp up faster.
TOKEN_COST_SHIFT_PER_RANGE_ABOVE_TARGET = 9.0
# Cost shift applied per 1x range width below target.
# Higher values make items below target drop faster.
TOKEN_COST_SHIFT_PER_RANGE_BELOW_TARGET = 1.0

#
# ITEM SELECTION AMOUNT RATIO SETTINGS
#

# Lower than 1.0 makes scrolls less likely to be selected in Potions and Scrolls.
# Example: 0.5 means scrolls get half the normal selection weight.
POTIONS_AND_SCROLLS_SCROLL_WEIGHT_MULTIPLIER = 0.1

# Big Six group weight tuning. Lower than 1.0 makes that group less likely.
# These only affect the Big Six table, where Armor and Weapon rows are weighted separately.
BIG_SIX_ARMOR_SPECIAL_MODIFIER = 0.02
BIG_SIX_WEAPON_SPECIAL_MODIFIER = 0.02


CSV_CONFIGS = [
	{
		"path": Path("big_six.csv"),
		"label": "Big Six",
		"token_csv_modifier": BIG_SIX_TOKEN_CSV_MODIFIER,
		"token_special_modifiers": BIG_SIX_TOKEN_SPECIAL_MODIFIERS,
		"armor_special_modifier": BIG_SIX_ARMOR_SPECIAL_MODIFIER,
		"weapon_special_modifier": BIG_SIX_WEAPON_SPECIAL_MODIFIER,
		"items_per_section": BIG_SIX_ITEMS_PER_SECTION,
		"range_width": BIG_SIX_ITEMVALUE_RANGE_WIDTH,
		"range_growth_per_level": BIG_SIX_ITEMVALUE_RANGE_GROWTH_PER_LEVEL,
	},
	{
		"path": Path("potions_and_scrolls.csv"),
		"token_csv_modifier": POTIONS_AND_SCROLLS_TOKEN_CSV_MODIFIER,
		"label": "Potions and Scrolls",
		"token_special_modifiers": POTIONS_AND_SCROLLS_TOKEN_SPECIAL_MODIFIERS,
		"scroll_weight_multiplier": POTIONS_AND_SCROLLS_SCROLL_WEIGHT_MULTIPLIER,
		"items_per_section": POTIONS_AND_SCROLLS_ITEMS_PER_SECTION,
		"range_width": POTIONS_AND_SCROLLS_ITEMVALUE_RANGE_WIDTH,
		"range_growth_per_level": POTIONS_AND_SCROLLS_ITEMVALUE_RANGE_GROWTH_PER_LEVEL,
	},
	{
		"path": Path("uniques.csv"),
		"label": "Uniques",
		"token_csv_modifier": UNIQUES_TOKEN_CSV_MODIFIER,
		"token_special_modifiers": UNIQUES_TOKEN_SPECIAL_MODIFIERS,
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


def token_cost_for_item(
	item_value: float,
	target_value: float,
	range_width: float,
	token_csv_modifier: float,
	item_group: str,
	token_special_modifiers: dict[str, float] | None = None,
) -> int:
	# Price items relative to current level target so on-level items remain affordable.
	effective_width = max(1.0, float(range_width))
	relative_delta = (float(item_value) - float(target_value)) / effective_width
	if relative_delta >= 0:
		shift_per_range = TOKEN_COST_SHIFT_PER_RANGE_ABOVE_TARGET
	else:
		shift_per_range = TOKEN_COST_SHIFT_PER_RANGE_BELOW_TARGET
	raw_cost = TOKEN_BASE_COST_AT_TARGET + (
		relative_delta * float(shift_per_range)
	)

	# Apply a CSV-wide token modifier before group-specific modifiers.
	raw_cost *= float(token_csv_modifier)

	# Apply item-group-based multipliers after the base price is computed.
	# If multiple keys match, their multipliers stack multiplicatively.
	group_name = str(item_group).strip().lower()
	for token_key, multiplier in (token_special_modifiers or {}).items():
		if token_key.strip().lower() == group_name:
			raw_cost *= float(multiplier)

	return max(1, min(10, int(round(raw_cost))))


def weighted_sample(
	frame: pd.DataFrame,
	target_value: float,
	range_width: float,
	scroll_weight_multiplier: float = 1.0,
	armor_special_modifier: float = 1.0,
	weapon_special_modifier: float = 1.0,
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

		if "Group" in remaining.columns:
			armor_mask = group_lower == "armor"
			weapon_mask = group_lower == "weapon"

			if armor_mask.any():
				weights = weights.where(
					~armor_mask,
					weights * max(0.0, float(armor_special_modifier)),
				)

			if weapon_mask.any():
				weights = weights.where(
					~weapon_mask,
					weights * max(0.0, float(weapon_special_modifier)),
				)

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
	token_csv_modifier: float,
	token_special_modifiers: dict[str, float] | None,
	target_value: float,
	range_width: float,
	debug_mode: bool,
) -> None:
	CONSOLE.print(f"\n[bold cyan]{label}[/bold cyan]")
	if items.empty:
		CONSOLE.print("[yellow]No items available.[/yellow]")
		return

	table = Table(show_header=True, header_style="bold", expand=True, show_lines=True)
	table.add_column("Name", ratio=1, min_width=18, overflow="fold")
	if debug_mode:
		table.add_column("CL", justify="right", width=6)
		table.add_column("PriceValue", justify="right", width=10)
		table.add_column("ItemValue", justify="right", width=10)
	table.add_column("Tokens", justify="right", width=8)
	table.add_column("Description", ratio=3, overflow="crop")

	# Estimate description width from console width so we can cap description to 3 lines.
	fixed_columns_width = 8 + (10 if debug_mode else 0)
	available_text_width = max(24, CONSOLE.width - fixed_columns_width - 12)
	# Use a slightly conservative wrap width so the final line does not spill over.
	description_wrap_width = max(16, int(available_text_width * 0.45))

	for number, (_, row) in enumerate(items.iterrows(), start=1):
		name = clean_description(row.get("Name", ""))
		description = clean_description(row.get("Description", ""))
		cl_value = clean_description(row.get("CL", ""))
		price_value = clean_description(row.get("PriceValue", ""))
		item_value = float(pd.to_numeric(row.get("ItemValue"), errors="coerce"))
		item_group = clean_description(row.get("Group", ""))
		tokens = token_cost_for_item(
			item_value,
			target_value,
			range_width,
			token_csv_modifier,
			item_group,
			token_special_modifiers,
		)
		name_text = name
		description_text = "\n".join(
			wrap_cell(description, description_wrap_width, max_lines=3)
		)

		if debug_mode:
			table.add_row(
				name_text,
				cl_value,
				price_value,
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
			armor_special_modifier=config.get("armor_special_modifier", 1.0),
			weapon_special_modifier=config.get("weapon_special_modifier", 1.0),
			count=config["items_per_section"],
		)
		print_shop_section(
			config["label"],
			items,
			config.get("token_csv_modifier", 1.0),
			config.get("token_special_modifiers"),
			target_value,
			range_width,
			DEBUG_MODE,
		)


if __name__ == "__main__":
	main()