from pathlib import Path

idea = Path("projects/IDEA.md").read_text(encoding="utf-8")
prompt = Path("templates/PROMPT_TEMPLATE.md").read_text(encoding="utf-8")

output = f"""
==================== SYSTEM ====================

{prompt}

==================== POMYSŁ ====================

{idea}
"""

Path("projects/FINAL_PROMPT.md").write_text(
    output,
    encoding="utf-8"
)

print("[OK] Utworzono FINAL_PROMPT.md")