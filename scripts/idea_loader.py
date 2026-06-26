from pathlib import Path

idea_path = Path("projects") / "IDEA.md"

if not idea_path.exists():
    print("[ERROR] Nie znaleziono IDEA.md")
    exit()

content = idea_path.read_text(encoding="utf-8")

print("=" * 60)
print("POMYSŁ")
print("=" * 60)
print(content)
print("=" * 60)