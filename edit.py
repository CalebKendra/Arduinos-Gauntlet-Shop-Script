import pandas as pd
from pathlib import Path
from collections import Counter
import re

df = pd.read_csv("source_csv/magicitems.csv")


def most_common_spell_level(spell_level_text):
	if pd.isna(spell_level_text):
		return None
	levels = [int(x) for x in re.findall(r"\d+", str(spell_level_text))]
	if not levels:
		return None
	return Counter(levels).most_common(1)[0][0]


def cl_from_spell_level(spell_level_text):
	level = most_common_spell_level(spell_level_text)
	if level is None:
		return pd.NA
	# CL = spell level +1 per level above 1st (e.g., 3rd -> CL 5)
	return max(1, 2 * level - 1)


def most_common_nonzero_price(row, columns):
	prices = []
	for column in columns:
		value = pd.to_numeric(row[column], errors="coerce")
		if pd.notna(value) and value > 0:
			prices.append(float(value))
	if not prices:
		fallback = pd.to_numeric(row.get("Lowest Scroll Cost"), errors="coerce")
		return float(fallback) if pd.notna(fallback) else pd.NA
	return Counter(prices).most_common(1)[0][0]

# Remove entries in ammunition/cursed groups and empty rows before splitting.
raw_group_lower = df["Group"].fillna("").str.lower()
raw_name_lower = df["Name"].fillna("").str.lower()
mask_remove_rows = (
	raw_group_lower.str.contains("ammunition|cursed", regex=True)
	| (raw_group_lower == "")
	| (raw_name_lower == "")
)
df = df[~mask_remove_rows].copy()

for output_file in [
	"big_six.csv",
	"potions_and_scrolls.csv",
	"uniques.csv",
]:
	Path(output_file).unlink(missing_ok=True)

name_lower = df["Name"].fillna("").str.lower()
name_key = name_lower.str.replace("’", "'", regex=False)
group_lower = df["Group"].fillna("").str.lower()

forced_potions_scrolls_names = {
	"feather token (anchor)",
	"universal solvent",
	"ioun torch",
	"stubborn nail",
	"war paint of the terrible visage",
	"elixir of love",
	"unguent of timelessness",
	"feather token (fan)",
	"formula alembic",
	"hybridization funnel",
	"soul soap",
	"dust of tracelessness",
	"elixir of hiding",
	"elixir of swimming",
	"elixir of tumbling",
	"elixir of vision",
	"nightdrops",
	"oil of silence",
	"silversheen",
	"traveler's any-tool",
	"bottle of messages",
	"feather token (bird)",
	"origami swarm",
	"alluring golden apple",
	"feather token (tree)",
	"key of lock jamming",
	"feather token (swan boat)",
	"animated portrait",
	"bottled misfortune",
	"elixir of truth",
	"feather token (whip)",
	"scabbard of honing",
	"seer's tea",
	"abjurant salt",
	"arrow magnet",
	"dust of darkness",
	"campfire bead",
	"archon's torch",
	"book of extended summoning, lesser",
	"iron rope",
	"snapleaf",
	"bottled yeti fur",
	"defoliant polish",
	"dust of emulation",
	"steadfast gut-stone",
	"dust of dryness",
	"anatomy doll",
	"bead of newt prevention",
	"beast-bond brand",
	"bookplate of recall",
	"boro bead (1st)",
	"concealing pocket",
	"dowsing syrup",
	"incense of transcendence",
	"page of spell knowledge (1st)",
	"pearl of power (1st)",
	"preserving flask (1st)",
	"pyxes of redirected focus",
	"salve of slipperiness",
	"wasp nest of swarming",
	"elixir of fire breath",
	"grave salt",
	"pipes of the sewers",
	"dust of illusion",
	"goblin skull bomb",
	"elixir of dragon breath",
	"bookmark of deception",
	"word bottle",
	"dust of acid consumption",
	"dust of appearance",
	"efficient quiver",
	"pipes of sounding",
	"scabbard of vigor",
	"agile alpenstock",
	"blood reservoir of physical prowess",
	"clamor box",
	"dry load powder horn",
	"goblin fire drum",
	"handy haversack",
	"horn of fog",
	"iron spike of safe passage",
	"knight's pennon, honor",
	"volatile vaporizer (1st)",
	"elemental gem",
	"flying ointment",
	"sovereign glue",
	"apple of eternal sleep",
	"bag of holding (type i)",
	"candle of truth",
	"hexing doll",
	"stone of alarm",
	"book of extended summoning, standard",
	"bead of force",
	"cauldron of brewing",
	"chime of opening",
	"philter of love",
	"rope of climbing",
	"volatile vaporizer (2nd)",
	"shroud of disintegration",
	"bag of tricks, gray",
	"dust of disappearance",
	"dust of weighty burdens",
	"noble's vigilant pillbox",
	"figurine of wondrous power (silver raven)",
	"volatile vaporizer (3rd)",
}

# CSV 1: cloak of resistance, ability belts/headbands, ring of protection,
# and amulet of natural armor.
ability_and_defense_patterns = [
	"cloak of resistance",
	"belt of giant strength",
	"belt of incredible dexterity",
	"belt of mighty constitution",
	"belt of physical might",
	"belt of physical perfection",
	"headband of alluring charisma",
	"headband of inspired wisdom",
	"headband of vast intelligence",
	"headband of mental prowess",
	"headband of mental superiority",
	"ring of protection",
	"amulet of natural armor",
]
mask_ability_and_defense = name_lower.str.contains(
	"|".join(ability_and_defense_patterns), regex=True
)
mask_ability_and_defense &= name_lower != "ring of protection from lycanthropy"

# CSV 2: all potions and scrolls.
mask_potions_and_scrolls = (
	group_lower.isin(["potion", "scroll"])
	| name_lower.str.startswith("potion of ")
	| name_lower.str.startswith("scroll of ")
	| name_lower.str.startswith("dust of ")
	| name_lower.str.startswith("metamagic gem")
	| name_lower.str.startswith("candle")
	| name_key.isin(forced_potions_scrolls_names)
)

ability_and_defense_df = df[mask_ability_and_defense].copy()
potions_and_scrolls_df = df[mask_potions_and_scrolls & ~mask_ability_and_defense].copy()
all_other_items_df = df[
	~(mask_ability_and_defense | mask_potions_and_scrolls)
].copy()

# Add extra potions from source_csv/potions.csv into Name and PriceValue.
potions_source_df = pd.read_csv("source_csv/potions.csv")
extra_potions = pd.DataFrame(columns=df.columns)
extra_potions["Name"] = potions_source_df["Potion or Oil"].fillna("").astype(str).str.strip()
extra_potions["PriceValue"] = pd.to_numeric(
	potions_source_df["Market Price"].astype(str).str.replace(",", "", regex=False),
	errors="coerce",
)
extra_potions["Group"] = "Potion"
extra_potions["Slot"] = "none"
extra_potions = extra_potions[
	(extra_potions["Name"] != "")
	& (extra_potions["Name"] != "-")
	& (extra_potions["Name"] != "—")
	& extra_potions["PriceValue"].notna()
].copy()

# Keep existing entries and add only missing potion names from the source table.
existing_names = set(potions_and_scrolls_df["Name"].fillna("").str.lower())
extra_potions = extra_potions[
	~extra_potions["Name"].str.lower().isin(existing_names)
].copy()
potions_and_scrolls_df = pd.concat(
	[potions_and_scrolls_df, extra_potions], ignore_index=True
)

# Add extra scrolls from source_csv/scrolls.csv.
scrolls_source_df = pd.read_csv("source_csv/scrolls.csv")
extra_scrolls = pd.DataFrame(columns=df.columns)
extra_scrolls["Name"] = scrolls_source_df["name"].fillna("").astype(str).str.strip()
extra_scrolls["Group"] = "Scroll"
extra_scrolls["Slot"] = "none"
extra_scrolls["Description"] = scrolls_source_df["shortDescription"]
extra_scrolls["CL"] = scrolls_source_df["spellLevel"].apply(cl_from_spell_level)

scroll_cost_columns = [
	"Cleric, Druid, Wizard Scroll Cost",
	"Sorcerer Scroll Cost",
	"Bard Scroll Cost",
	"Paladin, Ranger Scroll Cost",
]
extra_scrolls["PriceValue"] = scrolls_source_df.apply(
	lambda row: most_common_nonzero_price(row, scroll_cost_columns),
	axis=1,
)

extra_scrolls = extra_scrolls[
	(extra_scrolls["Name"] != "")
	& (extra_scrolls["Name"] != "-")
	& (extra_scrolls["Name"] != "—")
	& extra_scrolls["PriceValue"].notna()
].copy()

# Keep existing entries and add only missing scroll names from the source table.
existing_names = set(potions_and_scrolls_df["Name"].fillna("").str.lower())
extra_scrolls = extra_scrolls[
	~extra_scrolls["Name"].str.lower().isin(existing_names)
].copy()
potions_and_scrolls_df = pd.concat(
	[potions_and_scrolls_df, extra_scrolls], ignore_index=True
)

ability_and_defense_df.to_csv("big_six.csv", index=False)
potions_and_scrolls_df.to_csv("potions_and_scrolls.csv", index=False)
all_other_items_df.to_csv("uniques.csv", index=False)

print("Created files:")
print(f"- big_six.csv: {len(ability_and_defense_df)} rows")
print(f"- potions_and_scrolls.csv: {len(potions_and_scrolls_df)} rows")
print(f"  (including {len(extra_potions)} added from source_csv/potions.csv)")
print(f"  (including {len(extra_scrolls)} added from source_csv/scrolls.csv)")
print(f"- uniques.csv: {len(all_other_items_df)} rows")