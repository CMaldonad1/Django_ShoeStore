import os
import sys
import django
from pathlib import Path
from django.core.management import call_command

project_root = Path(__file__).resolve().parents[2]  # sube dos niveles desde botiga/seed
sys.path.append(str(project_root))

# start django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

#seed folder path
seed_folder = Path(__file__).parent
print(seed_folder)
files=seed_folder.glob("*.json")
print("Load seeders to Database:")
for f in files:
    print("Loading " + f.name)
    call_command('loaddata', str(f))

print("All seeders loaded.")