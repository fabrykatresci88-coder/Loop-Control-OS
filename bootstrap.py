from pathlib import Path

PROJECT_ROOT = Path.cwd()

folders = [
    "app",
    "bootstrap",
    "docs",
    "templates",
    "scripts",
    "archive",
]

for folder in folders:
    path = PROJECT_ROOT / folder
    path.mkdir(exist_ok=True)

print("[OK] Struktura utworzona.")