from pathlib import Path
import random
import textwrap

import pandas as pd
from rich.console import Console
from rich.table import Table


CONSOLE = Console()
SCRIPT_DIR = Path(__file__).resolve().parent


# Change this from 1 to 20 to bias the shop toward weaker or stronger items.
# THIS IS NOT USED IN APP.py
CHARACTER_LEVEL = 1

# Set to True to show target ItemValue and per-row ItemValue numbers.
DEBUG_MODE = False

#
# TARGET VALUE SCALING SETTINGS
#

# Determines the rate at which target ItemValue increasingly grows by level.
# Linear means the target ItemValue at level 20 will reach the ending value and at level 1 will match the starting value, with the curve shape determined by the exponent.
# 1.0 = linear, >1.0 grows slower early and faster later, <1.0 does the opposite.
TARGET_VALUE_SCALING_EXPONENT = 2.5

# Starting and ending target ItemValue for the level curve.
# Level 1 uses the starting value and level 20 uses the ending value.
TARGET_VALUE_START = 0.0
TARGET_VALUE_END = 75.0

#
# ITEMVALUE RANGE SETTINGS
#

# Controls how wide the offered ItemValue band is around the level target.
# Example: 15 means roughly target +/- 15 ItemValue.
BIG_SIX_ITEMVALUE_RANGE_WIDTH = 1.5
POTIONS_AND_SCROLLS_ITEMVALUE_RANGE_WIDTH = 5.0
UNIQUES_ITEMVALUE_RANGE_WIDTH = 0.5

# Maximum width allowed for each CSV's ItemValue band.
BIG_SIX_ITEMVALUE_RANGE_MAX = 15.0
POTIONS_AND_SCROLLS_ITEMVALUE_RANGE_MAX = 10.0
UNIQUES_ITEMVALUE_RANGE_MAX = 5.0

# Additional width added per level above 1.
# Example: 1.0 means level 10 adds +9 width.
BIG_SIX_ITEMVALUE_RANGE_GROWTH_PER_LEVEL = 0.5
POTIONS_AND_SCROLLS_ITEMVALUE_RANGE_GROWTH_PER_LEVEL = 0.7
UNIQUES_ITEMVALUE_RANGE_GROWTH_PER_LEVEL = 0.25

# Controls how strongly items closer to target ItemValue are favored during selection.
# 1.0 = standard inverse-distance weighting, >1.0 = strongly prefer items near target,
# <1.0 = items more evenly weighted regardless of distance.
TARGET_ITEMVALUE_CONCENTRATION = 1.2

#
# ITEMS PER SECTION SETTINGS
#

# Number of items to show per shop section.
BIG_SIX_ITEMS_PER_SECTION = 3
POTIONS_AND_SCROLLS_ITEMS_PER_SECTION = 4
UNIQUES_ITEMS_PER_SECTION = 5

#
# GROUP TOKEN COST SETTINGS
#

# Per-CSV token modifiers applied to every item in that CSV.
# 1.0 = no change, 1.2 = 20% more expensive, 0.8 = 20% cheaper.
BIG_SIX_TOKEN_CSV_MODIFIER = 1.7
POTIONS_AND_SCROLLS_TOKEN_CSV_MODIFIER = 0.5
UNIQUES_TOKEN_CSV_MODIFIER = 1.6

# Per-CSV level cost scales.
# 1.0 = no change across levels, 1.2 = gets 20% more expensive by level 20,
# 0.8 = gets 20% cheaper by level 20.
BIG_SIX_TOKEN_LEVEL_COST_SCALE = 1.0
POTIONS_AND_SCROLLS_TOKEN_LEVEL_COST_SCALE = 1.0
UNIQUES_TOKEN_LEVEL_COST_SCALE = 1.0


# Specific item group token cost modifiers.
# JSON-style token modifiers applied after the base relative price is calculated.
# Keys are checked as substrings against the item group, and matching entries multiply the final token cost.
BIG_SIX_TOKEN_SPECIAL_MODIFIERS = {
	'Weapon': 0.7,
	'Armor': 0.7,
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
# Cost shift applied per 1x range width above target for each CSV.
# Higher values make items above target ramp up faster.
BIG_SIX_TOKEN_COST_SHIFT_PER_RANGE_ABOVE_TARGET = 9.0
POTIONS_AND_SCROLLS_TOKEN_COST_SHIFT_PER_RANGE_ABOVE_TARGET = 9.0
UNIQUES_TOKEN_COST_SHIFT_PER_RANGE_ABOVE_TARGET = 9.0

# Cost shift applied per 1x range width below target for each CSV.
# Higher values make items below target drop faster.
BIG_SIX_TOKEN_COST_SHIFT_PER_RANGE_BELOW_TARGET = 1.0
POTIONS_AND_SCROLLS_TOKEN_COST_SHIFT_PER_RANGE_BELOW_TARGET = 2.0
UNIQUES_TOKEN_COST_SHIFT_PER_RANGE_BELOW_TARGET = 2.5

#
# ITEM SELECTION AMOUNT RATIO SETTINGS
#

# Lower than 1.0 makes scrolls less likely to be selected in Potions and Scrolls.
# Example: 0.5 means scrolls get half the normal selection weight.
POTIONS_AND_SCROLLS_SCROLL_WEIGHT_MULTIPLIER = 0.08

# Lower than 1.0 makes potions less likely to be selected in Potions and Scrolls.
# Example: 0.5 means potions get half the normal selection weight.
POTIONS_AND_SCROLLS_POTION_WEIGHT_MULTIPLIER = 0.5

# Special Ability percent chance modifier. Lower than 1.0 makes that group less likely.
# These only affect the Big Six table, where Armor and Weapon rows are weighted separately.
BIG_SIX_ARMOR_SPECIAL_MODIFIER = 0.07
BIG_SIX_WEAPON_SPECIAL_MODIFIER = 0.07


CSV_CONFIGS = [
	{
		"path": SCRIPT_DIR / "big_six.csv",
		"label": "Big Six",
		"token_csv_modifier": BIG_SIX_TOKEN_CSV_MODIFIER,
		"token_level_cost_scale": BIG_SIX_TOKEN_LEVEL_COST_SCALE,
		"token_shift_above_target": BIG_SIX_TOKEN_COST_SHIFT_PER_RANGE_ABOVE_TARGET,
		"token_shift_below_target": BIG_SIX_TOKEN_COST_SHIFT_PER_RANGE_BELOW_TARGET,
		"token_special_modifiers": BIG_SIX_TOKEN_SPECIAL_MODIFIERS,
		"armor_special_modifier": BIG_SIX_ARMOR_SPECIAL_MODIFIER,
		"weapon_special_modifier": BIG_SIX_WEAPON_SPECIAL_MODIFIER,
		"items_per_section": BIG_SIX_ITEMS_PER_SECTION,
		"range_width": BIG_SIX_ITEMVALUE_RANGE_WIDTH,
		"range_growth_per_level": BIG_SIX_ITEMVALUE_RANGE_GROWTH_PER_LEVEL,
		"range_max": BIG_SIX_ITEMVALUE_RANGE_MAX,
	},
	{
		"path": SCRIPT_DIR / "potions_and_scrolls.csv",
		"token_csv_modifier": POTIONS_AND_SCROLLS_TOKEN_CSV_MODIFIER,
		"label": "Potions, Scrolls, and Temporary Tools",
		"token_level_cost_scale": POTIONS_AND_SCROLLS_TOKEN_LEVEL_COST_SCALE,
		"token_shift_above_target": POTIONS_AND_SCROLLS_TOKEN_COST_SHIFT_PER_RANGE_ABOVE_TARGET,
		"token_shift_below_target": POTIONS_AND_SCROLLS_TOKEN_COST_SHIFT_PER_RANGE_BELOW_TARGET,
		"token_special_modifiers": POTIONS_AND_SCROLLS_TOKEN_SPECIAL_MODIFIERS,
		"scroll_weight_multiplier": POTIONS_AND_SCROLLS_SCROLL_WEIGHT_MULTIPLIER,
		"potion_weight_multiplier": POTIONS_AND_SCROLLS_POTION_WEIGHT_MULTIPLIER,
		"items_per_section": POTIONS_AND_SCROLLS_ITEMS_PER_SECTION,
		"range_width": POTIONS_AND_SCROLLS_ITEMVALUE_RANGE_WIDTH,
		"range_growth_per_level": POTIONS_AND_SCROLLS_ITEMVALUE_RANGE_GROWTH_PER_LEVEL,
		"range_max": POTIONS_AND_SCROLLS_ITEMVALUE_RANGE_MAX,
	},
	{
		"path": SCRIPT_DIR / "uniques.csv",
		"label": "Uniques",
		"token_csv_modifier": UNIQUES_TOKEN_CSV_MODIFIER,
		"token_level_cost_scale": UNIQUES_TOKEN_LEVEL_COST_SCALE,
		"token_shift_above_target": UNIQUES_TOKEN_COST_SHIFT_PER_RANGE_ABOVE_TARGET,
		"token_shift_below_target": UNIQUES_TOKEN_COST_SHIFT_PER_RANGE_BELOW_TARGET,
		"token_special_modifiers": UNIQUES_TOKEN_SPECIAL_MODIFIERS,
		"items_per_section": UNIQUES_ITEMS_PER_SECTION,
		"range_width": UNIQUES_ITEMVALUE_RANGE_WIDTH,
		"range_growth_per_level": UNIQUES_ITEMVALUE_RANGE_GROWTH_PER_LEVEL,
		"range_max": UNIQUES_ITEMVALUE_RANGE_MAX,
	},
]


def level_to_target_value(level: int) -> float:
	level = max(1, min(20, int(level)))
	normalized_level = (level - 1) / 19
	exponent = max(0.01, float(TARGET_VALUE_SCALING_EXPONENT))
	start_value = float(TARGET_VALUE_START)
	end_value = float(TARGET_VALUE_END)
	return start_value + (((normalized_level**exponent) * (end_value - start_value)))


def level_to_range_width(
	level: int,
	base_width: float,
	growth_per_level: float,
	range_max: float,
) -> float:
	level = max(1, min(20, int(level)))
	width = float(base_width) + ((level - 1) * float(growth_per_level))
	return max(0.0, min(float(range_max), width))


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
	character_level: int,
	token_csv_modifier: float,
	token_level_cost_scale: float,
	token_shift_above_target: float,
	token_shift_below_target: float,
	item_group: str,
	token_special_modifiers: dict[str, float] | None = None,
) -> int:
	# Price items relative to current level target so on-level items remain affordable.
	effective_width = max(1.0, float(range_width))
	relative_delta = (float(item_value) - float(target_value)) / effective_width
	if relative_delta >= 0:
		shift_per_range = float(token_shift_above_target)
	else:
		shift_per_range = float(token_shift_below_target)
	raw_cost = TOKEN_BASE_COST_AT_TARGET + (
		relative_delta * shift_per_range
	)

	# Apply a CSV-wide token modifier before group-specific modifiers.
	raw_cost *= float(token_csv_modifier)

	# Apply a per-CSV level multiplier so the table can scale up or down over time.
	level_progress = (max(1, min(20, int(character_level))) - 1) / 19
	level_cost_multiplier = 1.0 + (level_progress * (float(token_level_cost_scale) - 1.0))
	raw_cost *= level_cost_multiplier

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
	potion_weight_multiplier: float = 1.0,
	armor_special_modifier: float = 1.0,
	weapon_special_modifier: float = 1.0,
	target_itemvalue_concentration: float = 1.0,
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
		weights = 1 / ((1 + distances) ** float(target_itemvalue_concentration))

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

		# Apply potion weight multiplier if potion group or name is detected.
		if "Group" in remaining.columns:
			potion_mask = group_lower == "potion"
		elif "Name" in remaining.columns:
			name_lower = remaining["Name"].fillna("").astype(str).str.lower().str.strip()
			potion_mask = name_lower.str.startswith("potion of ")
		else:
			potion_mask = pd.Series(False, index=remaining.index)

		if potion_mask.any():
			weights = weights.where(~potion_mask, weights * max(0.0, float(potion_weight_multiplier)))

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
	character_level: int,
	token_csv_modifier: float,
	token_level_cost_scale: float,
	token_shift_above_target: float,
	token_shift_below_target: float,
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
			character_level,
			token_csv_modifier,
			token_level_cost_scale,
			token_shift_above_target,
			token_shift_below_target,
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
				config["range_max"],
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
			config["range_max"],
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
			potion_weight_multiplier=config.get("potion_weight_multiplier", 1.0),
			armor_special_modifier=config.get("armor_special_modifier", 1.0),
			weapon_special_modifier=config.get("weapon_special_modifier", 1.0),
			target_itemvalue_concentration=TARGET_ITEMVALUE_CONCENTRATION,
			count=config["items_per_section"],
		)
		print_shop_section(
			config["label"],
			items,
			CHARACTER_LEVEL,
			config.get("token_csv_modifier", 1.0),
			config.get("token_level_cost_scale", 1.0),
			config.get("token_shift_above_target", 9.0),
			config.get("token_shift_below_target", 2.0),
			config.get("token_special_modifiers"),
			target_value,
			range_width,
			DEBUG_MODE,
		)


if __name__ == "__main__":
	main()