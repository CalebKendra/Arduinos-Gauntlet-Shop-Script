from pathlib import Path

import pandas as pd


CSV_FILES = ["big_six.csv", "potions_and_scrolls.csv", "uniques.csv"]
SCRIPT_DIR = Path(__file__).resolve().parent

# Lower values compress ItemValue toward the mean; higher values spread it out.
ITEMVALUE_STDDEV_SCALE = 1.0
# Values above 1.0 make high ItemValue items grow faster than low ones.
ITEMVALUE_EXPONENT = 1.0


def min_max_scale(series: pd.Series) -> pd.Series:
	numeric = pd.to_numeric(series, errors="coerce")
	valid = numeric.dropna()
	if valid.empty:
		return pd.Series([0.0] * len(series), index=series.index)
	minimum = valid.min()
	maximum = valid.max()
	if minimum == maximum:
		return pd.Series([100.0] * len(series), index=series.index)
	return ((numeric - minimum) / (maximum - minimum) * 100).fillna(0.0)


def clean_cl(series: pd.Series) -> pd.Series:
	cleaned = series.astype(str).str.strip().str.lower()
	cleaned = cleaned.replace({"varies": pd.NA, "": pd.NA, "nan": pd.NA, "none": pd.NA})
	return pd.to_numeric(cleaned, errors="coerce")


def clean_price(series: pd.Series) -> pd.Series:
	numeric = pd.to_numeric(series, errors="coerce")
	return numeric.where(numeric > 0)


def apply_stddev_spread(series: pd.Series, scale: float) -> pd.Series:
	numeric = pd.to_numeric(series, errors="coerce")
	valid = numeric.dropna()
	if valid.empty:
		return pd.Series([0.0] * len(series), index=series.index)
	mean = valid.mean()
	stddev = valid.std(ddof=0)
	if stddev == 0 or scale == 1.0:
		return numeric.fillna(0.0)
	adjusted = mean + ((numeric - mean) * scale)
	return adjusted.clip(0, 100).fillna(0.0)


def apply_exponential_curve(series: pd.Series, exponent: float) -> pd.Series:
	numeric = pd.to_numeric(series, errors="coerce").fillna(0.0).clip(0, 100)
	if exponent == 1.0:
		return numeric
	normalized = numeric / 100.0
	curved = normalized.pow(exponent)
	return (curved * 100).clip(0, 100)


def compute_item_value(frame: pd.DataFrame) -> pd.DataFrame:
	result = frame.copy()
	if "CL" not in result.columns:
		result["CL"] = pd.NA
	if "PriceValue" not in result.columns:
		result["PriceValue"] = pd.NA
	result["CL"] = clean_cl(result["CL"])
	result["PriceValue"] = clean_price(result["PriceValue"])

	cl_score = min_max_scale(result["CL"])
	price_score = min_max_scale(result["PriceValue"])

	has_cl = result["CL"].notna()
	has_price = result["PriceValue"].notna()
	result["ItemValue"] = 0.0

	only_cl = has_cl & ~has_price
	any_price = has_price

	# If PriceValue exists, it fully determines ItemValue; CL is only a fallback.
	result.loc[any_price, "ItemValue"] = price_score[any_price]
	result.loc[only_cl, "ItemValue"] = cl_score[only_cl]
	result["ItemValue"] = apply_stddev_spread(result["ItemValue"], ITEMVALUE_STDDEV_SCALE)
	result["ItemValue"] = apply_exponential_curve(result["ItemValue"], ITEMVALUE_EXPONENT).round(2)
	return result


def process_file(path: Path) -> None:
	frame = pd.read_csv(path)
	frame = compute_item_value(frame)
	frame.to_csv(path, index=False)
	print(f"Updated {path.name}: {len(frame)} rows")


def main() -> None:
	for file_name in CSV_FILES:
		path = SCRIPT_DIR / file_name
		if not path.exists():
			print(f"Skipped {file_name}: file not found")
			continue
		process_file(path)


if __name__ == "__main__":
	main()