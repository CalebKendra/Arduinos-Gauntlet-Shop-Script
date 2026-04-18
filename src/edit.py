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


def armor_special_price_to_value(base_price_text):
	text = str(base_price_text).strip()
	flat_price_match = re.fullmatch(r"\+(\d[\d,]*)", text)
	if flat_price_match:
		return int(flat_price_match.group(1).replace(",", ""))

	bonus_match = re.fullmatch(r"\+(\d+)\s+bonus", text)
	if bonus_match:
		bonus = int(bonus_match.group(1))
		return int((bonus*bonus) * 1000)

	return pd.NA


def bonus_from_base_price_modifier(base_price_text):
	text = str(base_price_text).strip()
	bonus_match = re.fullmatch(r"\+(\d+)\s+bonus", text)
	if not bonus_match:
		return None
	return int(bonus_match.group(1))

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

# Add simple magic weapon entries to the Big Six table.
extra_magic_weapons = pd.DataFrame(columns=df.columns)
extra_magic_weapons["Name"] = [
	"+1 Magic Weapon",
	"+2 Magic Weapon",
	"+3 Magic Weapon",
]
extra_magic_weapons["CL"] = (
	extra_magic_weapons["Name"].str.extract(r"\+(\d+)", expand=False).astype(int) * 3
)
extra_magic_weapons["PriceValue"] = [2000, 8000, 18000]
extra_magic_weapons["Group"] = "Weapon Upgrade"
extra_magic_weapons["Slot"] = "none"

existing_big_six_names = set(ability_and_defense_df["Name"].fillna("").str.lower())
extra_magic_weapons = extra_magic_weapons[
	~extra_magic_weapons["Name"].str.lower().isin(existing_big_six_names)
].copy()
ability_and_defense_df = pd.concat(
	[ability_and_defense_df, extra_magic_weapons], ignore_index=True
)

# Add simple magic armor entries to the Big Six table.
extra_magic_armor = pd.DataFrame(columns=df.columns)
extra_magic_armor["Name"] = [
	"+1 Magic Armor",
	"+2 Magic Armor",
	"+3 Magic Armor",
]
extra_magic_armor["CL"] = (
	extra_magic_armor["Name"].str.extract(r"\+(\d+)", expand=False).astype(int) * 3
)
extra_magic_armor["PriceValue"] = [1000, 4000, 9000]
extra_magic_armor["Group"] = "Armor Upgrade"
extra_magic_armor["Slot"] = "armor"

existing_big_six_names = set(ability_and_defense_df["Name"].fillna("").str.lower())
extra_magic_armor = extra_magic_armor[
	~extra_magic_armor["Name"].str.lower().isin(existing_big_six_names)
].copy()
ability_and_defense_df = pd.concat(
	[ability_and_defense_df, extra_magic_armor], ignore_index=True
)

# Add armor special abilities from the provided tables.
armor_special_abilities = [
	(1, "Benevolent", "+2,000"),
	(1, "Billowing", "+1 bonus"),
	(1, "Cocooning", "+1 bonus"),
	(1, "Poison-resistant", "+2,250"),
	(1, "Balanced", "+1 bonus"),
	(1, "Bitter", "+1 bonus"),
	(1, "Bolstering", "+1 bonus"),
	(1, "Champion", "+1 bonus"),
	(1, "Dastard", "+1 bonus"),
	(1, "Deathless", "+1 bonus"),
	(1, "Defiant", "+1 bonus"),
	(1, "Fortification (light)", "+1 bonus"),
	(1, "Grinding", "+1 bonus"),
	(1, "Impervious", "+1 bonus"),
	(1, "Mirrored", "+1 bonus"),
	(1, "Spell storing", "+1 bonus"),
	(1, "Stanching", "+1 bonus"),
	(1, "Warding", "+1 bonus"),
	(2, "Glamered", "+2,700"),
	(2, "Jousting", "+3,750"),
	(2, "Shadow", "+3,750"),
	(2, "Slick", "+3,750"),
	(2, "Expeditious", "+4,000"),
	(2, "Creeping", "+5,000"),
	(2, "Rallying", "+5,000"),
	(2, "Spell resistance (13)", "+2 bonus"),
	(3, "Adhesive", "+7,000"),
	(3, "Cotraveling", "+3 bonus"),
	(3, "Brawling", "+3 bonus"),
	(3, "Hosteling", "+7,500"),
	(3, "Radiant", "+7,500"),
	(3, "Delving", "+10,000"),
	(3, "Putrid", "+10,000"),
	(3, "Fortification (moderate)", "+3 bonus"),
	(3, "Ghost touch", "+3 bonus"),
	(3, "Invulnerability", "+3 bonus"),
	(3, "Shadow blending", "+3 bonus"),
	(3, "Spell resistance (15)", "+3 bonus"),
	(3, "Titanic", "+3 bonus"),
	(3, "Wild", "+3 bonus"),
	(4, "Harmonizing", "+15,000"),
	(4, "Shadow, improved", "+15,000"),
	(4, "Slick, improved", "+15,000"),
	(4, "Energy resistance", "+18,000"),
	(4, "Martyring", "+18,000"),
	(4, "Spell resistance (17)", "+4 bonus"),
	(5, "Righteous", "+27,000"),
	(5, "Unbound", "+27,000"),
	(5, "Unrighteous", "+27,000"),
	(5, "Vigilant", "+27,000"),
	(5, "Determination", "+30,000"),
	(5, "Shadow, greater", "+33,750"),
	(5, "Slick, greater", "+33,750"),
	(5, "Energy resistance, improved", "+42,000"),
	(5, "Etherealness", "+49,000"),
	(5, "Undead controlling", "+49,000"),
	(5, "Energy resistance, greater", "+66,000"),
	(5, "Fortification (heavy)", "+5 bonus"),
	(5, "Spell resistance (19)", "+5 bonus"),
]

armor_special_cl_by_name = {
	"Benevolent": 5,
	"Billowing": 3,
	"Cocooning": 9,
	"Poison-resistant": 7,
	"Balanced": 5,
	"Bitter": 5,
	"Bolstering": 5,
	"Champion": 5,
	"Dastard": 5,
	"Deathless": 7,
	"Defiant": 8,
	"Fortification (light)": 13,
	"Grinding": 5,
	"Impervious": 7,
	"Mirrored": 8,
	"Spell storing": 12,
	"Stanching": 7,
	"Warding": 12,
	"Glamered": 10,
	"Jousting": 5,
	"Shadow": 5,
	"Slick": 4,
	"Expeditious": 5,
	"Creeping": 7,
	"Rallying": 5,
	"Spell resistance (13)": 15,
	"Adhesive": 10,
	"Cotraveling": 14,
	"Brawling": 5,
	"Hosteling": 9,
	"Radiant": 6,
	"Delving": 5,
	"Putrid": 5,
	"Fortification (moderate)": 13,
	"Ghost touch": 15,
	"Invulnerability": 18,
	"Shadow blending": 11,
	"Spell resistance (15)": 15,
	"Titanic": 7,
	"Wild": 9,
	"Harmonizing": 7,
	"Shadow, improved": 10,
	"Slick, improved": 10,
	"Energy resistance": 3,
	"Martyring": 9,
	"Spell resistance (17)": 15,
	"Righteous": 10,
	"Unbound": 10,
	"Unrighteous": 10,
	"Vigilant": 10,
	"Determination": 10,
	"Shadow, greater": 15,
	"Slick, greater": 15,
	"Energy resistance, improved": 7,
	"Etherealness": 13,
	"Undead controlling": 13,
	"Energy resistance, greater": 11,
	"Fortification (heavy)": 13,
	"Spell resistance (19)": 15,
}

armor_special_df = pd.DataFrame(columns=df.columns)
armor_special_df["Name"] = [
	f"+{item[1]} Magic Armor" for item in armor_special_abilities
]
armor_special_df["CL"] = [armor_special_cl_by_name[item[1]] for item in armor_special_abilities]
armor_special_df["PriceValue"] = [
	armor_special_price_to_value(item[2]) for item in armor_special_abilities
]
armor_special_df["Group"] = "Armor"
armor_special_df["Slot"] = "armor"

existing_big_six_names = set(ability_and_defense_df["Name"].fillna("").str.lower())
armor_special_df = armor_special_df[
	~armor_special_df["Name"].str.lower().isin(existing_big_six_names)
].copy()
ability_and_defense_df = pd.concat(
	[ability_and_defense_df, armor_special_df], ignore_index=True
)

# Add weapon special abilities from the provided tables.
weapon_special_abilities = [
	(1, "Impervious", "+3,000"),
	(1, "Glamered", "+4,000"),
	(1, "Allying", "+1 bonus"),
	(1, "Bane", "+1 bonus"),
	(1, "Benevolent", "+1 bonus"),
	(1, "Called", "+1 bonus"),
	(1, "Conductive", "+1 bonus"),
	(1, "Corrosive", "+1 bonus"),
	(1, "Countering", "+1 bonus"),
	(1, "Courageous", "+1 bonus"),
	(1, "Cruel", "+1 bonus"),
	(1, "Cunning", "+1 bonus"),
	(1, "Deadly", "+1 bonus"),
	(1, "Defending", "+1 bonus"),
	(1, "Dispelling", "+1 bonus"),
	(1, "Flaming", "+1 bonus"),
	(1, "Frost", "+1 bonus"),
	(1, "Furious", "+1 bonus"),
	(1, "Ghost touch", "+1 bonus"),
	(1, "Grayflame", "+1 bonus"),
	(1, "Grounding", "+1 bonus"),
	(1, "Guardian", "+1 bonus"),
	(1, "Heartseeker", "+1 bonus"),
	(1, "Huntsman", "+1 bonus"),
	(1, "Jurist", "+1 bonus"),
	(1, "Keen", "+1 bonus"),
	(1, "Ki focus", "+1 bonus"),
	(1, "Limning", "+1 bonus"),
	(1, "Menacing", "+1 bonus"),
	(1, "Merciful", "+1 bonus"),
	(1, "Mighty cleaving", "+1 bonus"),
	(1, "Mimetic", "+1 bonus"),
	(1, "Neutralizing", "+1 bonus"),
	(1, "Ominous", "+1 bonus"),
	(1, "Planar", "+1 bonus"),
	(1, "Quenching", "+1 bonus"),
	(1, "Seaborne", "+1 bonus"),
	(1, "Shock", "+1 bonus"),
	(1, "Spell storing", "+1 bonus"),
	(1, "Thawing", "+1 bonus"),
	(1, "Throwing", "+1 bonus"),
	(1, "Thundering", "+1 bonus"),
	(1, "Unaligned", "+1 bonus"),
	(1, "Valiant", "+1 bonus"),
	(1, "Vicious", "+1 bonus"),
	(2, "Advancing", "+2 bonus"),
	(2, "Anarchic", "+2 bonus"),
	(2, "Anchoring", "+2 bonus"),
	(2, "Axiomatic", "+2 bonus"),
	(2, "Corrosive burst", "+2 bonus"),
	(2, "Defiant", "+2 bonus"),
	(2, "Dispelling burst", "+2 bonus"),
	(2, "Disruption", "+2 bonus"),
	(2, "Flaming burst", "+2 bonus"),
	(2, "Furyborn", "+2 bonus"),
	(2, "Glorious", "+2 bonus"),
	(2, "Holy", "+2 bonus"),
	(2, "Icy burst", "+2 bonus"),
	(2, "Igniting", "+2 bonus"),
	(2, "Impact", "+2 bonus"),
	(2, "Invigorating", "+2 bonus"),
	(2, "Ki intensifying", "+2 bonus"),
	(2, "Lifesurge", "+2 bonus"),
	(2, "Negating", "+2 bonus"),
	(2, "Phase locking", "+2 bonus"),
	(2, "Planestriking", "+2 bonus"),
	(2, "Shocking burst", "+2 bonus"),
	(2, "Stalking", "+2 bonus"),
	(2, "Unholy", "+2 bonus"),
	(2, "Wounding", "+2 bonus"),
	(3, "Nullifying", "+3 bonus"),
	(3, "Repositioning", "+3 bonus"),
	(3, "Speed", "+3 bonus"),
	(3, "Spell stealing", "+3 bonus"),
	(4, "Brilliant energy", "+4 bonus"),
	(4, "Dancing", "+4 bonus"),
	(5, "Vorpal", "+5 bonus"),
	(4, "Transformative", "+10,000"),
	(4, "Dueling", "+14,000"),
	(1, "Adaptive", "+1,000"),
	(1, "Conserving", "+1 bonus"),
	(1, "Distance", "+1 bonus"),
	(1, "Lucky", "+1 bonus"),
	(1, "Reliable", "+1 bonus"),
	(1, "Returning", "+1 bonus"),
	(1, "Seeking", "+1 bonus"),
	(2, "Designating, lesser", "+2 bonus"),
	(2, "Endless ammunition", "+2 bonus"),
	(3, "Lucky, greater", "+3 bonus"),
	(3, "Reliable, greater", "+3 bonus"),
	(4, "Designating, greater", "+4 bonus"),
	(4, "Nimble shot", "+4 bonus"),
	(4, "Second chance", "+4 bonus"),
]

weapon_special_cl_by_name = {
	"+Impervious Magic Weapon": 7,
	"+Glamered Magic Weapon": 10,
	"+Allying Magic Weapon": 5,
	"+Bane Magic Weapon": 8,
	"+Benevolent Magic Weapon": 5,
	"+Called Magic Weapon": 9,
	"+Conductive Magic Weapon": 8,
	"+Corrosive Magic Weapon": 10,
	"+Countering Magic Weapon": 5,
	"+Courageous Magic Weapon": 3,
	"+Cruel Magic Weapon": 5,
	"+Cunning Magic Weapon": 6,
	"+Deadly Magic Weapon": 5,
	"+Defending Magic Weapon": 8,
	"+Dispelling Magic Weapon": 10,
	"+Flaming Magic Weapon": 10,
	"+Frost Magic Weapon": 8,
	"+Furious Magic Weapon": 8,
	"+Ghost touch Magic Weapon": 9,
	"+Grayflame Magic Weapon": 6,
	"+Grounding Magic Weapon": 5,
	"+Guardian Magic Weapon": 8,
	"+Heartseeker Magic Weapon": 7,
	"+Huntsman Magic Weapon": 7,
	"+Jurist Magic Weapon": 4,
	"+Keen Magic Weapon": 10,
	"+Ki focus Magic Weapon": 8,
	"+Limning Magic Weapon": 5,
	"+Menacing Magic Weapon": 10,
	"+Merciful Magic Weapon": 5,
	"+Mighty cleaving Magic Weapon": 8,
	"+Mimetic Magic Weapon": 5,
	"+Neutralizing Magic Weapon": 5,
	"+Ominous Magic Weapon": 5,
	"+Planar Magic Weapon": 9,
	"+Quenching Magic Weapon": 5,
	"+Seaborne Magic Weapon": 7,
	"+Shock Magic Weapon": 8,
	"+Spell storing Magic Weapon": 12,
	"+Thawing Magic Weapon": 5,
	"+Throwing Magic Weapon": 5,
	"+Thundering Magic Weapon": 5,
	"+Unaligned Magic Weapon": 5,
	"+Valiant Magic Weapon": 5,
	"+Vicious Magic Weapon": 9,
	"+Advancing Magic Weapon": 5,
	"+Anarchic Magic Weapon": 7,
	"+Anchoring Magic Weapon": 10,
	"+Axiomatic Magic Weapon": 7,
	"+Corrosive burst Magic Weapon": 12,
	"+Defiant Magic Weapon": 10,
	"+Dispelling burst Magic Weapon": 12,
	"+Disruption Magic Weapon": 14,
	"+Flaming burst Magic Weapon": 12,
	"+Furyborn Magic Weapon": 7,
	"+Glorious Magic Weapon": 5,
	"+Holy Magic Weapon": 7,
	"+Icy burst Magic Weapon": 10,
	"+Igniting Magic Weapon": 12,
	"+Impact Magic Weapon": 9,
	"+Invigorating Magic Weapon": 5,
	"+Ki intensifying Magic Weapon": 12,
	"+Lifesurge Magic Weapon": 8,
	"+Negating Magic Weapon": 5,
	"+Phase locking Magic Weapon": 7,
	"+Planestriking Magic Weapon": 9,
	"+Shocking burst Magic Weapon": 10,
	"+Stalking Magic Weapon": 10,
	"+Unholy Magic Weapon": 7,
	"+Wounding Magic Weapon": 10,
	"+Nullifying Magic Weapon": 12,
	"+Repositioning Magic Weapon": 10,
	"+Speed Magic Weapon": 7,
	"+Spell stealing Magic Weapon": 13,
	"+Brilliant energy Magic Weapon": 16,
	"+Dancing Magic Weapon": 15,
	"+Vorpal Magic Weapon": 18,
	"+Transformative Magic Weapon": 10,
	"+Dueling Magic Weapon": 5,
	"+Adaptive Magic Weapon": 1,
	"+Conserving Magic Weapon": 7,
	"+Distance Magic Weapon": 6,
	"+Lucky Magic Weapon": 8,
	"+Reliable Magic Weapon": 8,
	"+Returning Magic Weapon": 7,
	"+Seeking Magic Weapon": 12,
	"+Designating, lesser Magic Weapon": 7,
	"+Endless ammunition Magic Weapon": 9,
	"+Lucky, greater Magic Weapon": 12,
	"+Reliable, greater Magic Weapon": 12,
	"+Designating, greater Magic Weapon": 12,
	"+Nimble shot Magic Weapon": 11,
	"+Second chance Magic Weapon": 11,
}

weapon_special_df = pd.DataFrame(columns=df.columns)
weapon_special_df["Name"] = [
	f"+{item[1]} Magic Weapon" for item in weapon_special_abilities
]
weapon_special_df["CL"] = [weapon_special_cl_by_name[name] for name in weapon_special_df["Name"]]
weapon_special_df["PriceValue"] = [
	armor_special_price_to_value(item[2]) for item in weapon_special_abilities
]
weapon_special_df["Group"] = "Weapon"
weapon_special_df["Slot"] = "none"

existing_big_six_names = set(ability_and_defense_df["Name"].fillna("").str.lower())
weapon_special_df = weapon_special_df[
	~weapon_special_df["Name"].str.lower().isin(existing_big_six_names)
].copy()
ability_and_defense_df = pd.concat(
	[ability_and_defense_df, weapon_special_df], ignore_index=True
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