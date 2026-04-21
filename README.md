# Arduino's Gauntlet

## Create Build

```
python.exe -m PyInstaller --noconfirm --onefile --windowed --name arduinosgauntlet --distpath . --workpath build --specpath . --hidden-import rich --hidden-import rich.console --hidden-import rich.table arduinosgauntlet_launcher.py
```
