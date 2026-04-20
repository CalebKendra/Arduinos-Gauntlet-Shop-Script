# Arduino's Gauntlet Shop Script

## PySide6 GUI App

The project now includes a desktop GUI at src/app.py.

Install dependencies:

```bash
pip install pandas PySide6 rich
```

Run the GUI from the repository root:

```bash
py src/app.py
```

### Features

- Shop tab:
	- Uses the same weighted item generation and token pricing logic from src/shop/shop.py.
	- Starts the player with 10 tokens.
	- Lets the player buy selected items from each section.
	- Lets the player reroll all shop sections for 1 token.

- Boons tab:
	- Lets the player choose Martial or Caster.
	- Rolls 3 boons from the selected type plus General boons.
