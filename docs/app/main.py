from pathlib import Path

print("=" * 60)
print("LOOP CONTROL OS")
print("=" * 60)

idea = Path("projects/IDEA.md").read_text(encoding="utf-8")

print(idea)

print("=" * 60)
print("System gotowy.")