"""
list_commands.py — Generate ready-to-run command files for each novel in content.

Output: novelhall\commands\<novel-slug>.txt

Run from the project root:
    venv/Scripts/python.exe novelhall/list_commands.py
"""

from pathlib import Path

CONTENT_DIR = Path(__file__).parent / "content"
COMMANDS_DIR = Path(__file__).parent / "commands"
PREFIX = r"venv\Scripts\python.exe novelhall\novelhall.py"


def main():
    COMMANDS_DIR.mkdir(exist_ok=True)

    novels = sorted(d for d in CONTENT_DIR.iterdir() if d.is_dir())
    if not novels:
        print("No novels found in content folder.")
        return

    for novel in novels:
        chapters = sorted(novel.glob("chapter-*.txt"))
        if not chapters:
            continue

        lines = []
        lines.append(f"{PREFIX} novelhall\\content\\{novel.name}")
        for ch in chapters:
            lines.append(f"{PREFIX} novelhall\\content\\{novel.name}\\{ch.name}")

        out_path = COMMANDS_DIR / f"{novel.name}.txt"
        out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"Written: {out_path}  ({len(chapters)} chapter(s))")

    print("\nDone.")


if __name__ == "__main__":
    main()
