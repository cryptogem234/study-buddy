"""
generate_visuals.py
Generates one labeled educational diagram per lesson in a given subject using
Claude's code execution tool (matplotlib), saves it to backend/static/<subject>/,
and embeds it into the lesson's markdown content (under "## Core Concepts").

Skips lessons that already have an embedded image.

Run from the backend folder:
    python generate_visuals.py [SubjectName]

    SubjectName defaults to "Chemistry" if omitted.

Requires backend/.env:
    ANTHROPIC_API_KEY=sk-ant-...
"""
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
import anthropic
from database import SessionLocal
import models

load_dotenv(Path(__file__).parent / ".env")

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not API_KEY:
    print("ERROR: ANTHROPIC_API_KEY not found in backend/.env")
    exit(1)

client = anthropic.Anthropic(api_key=API_KEY)

MODEL = "claude-sonnet-4-6"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".svg"}

DIAGRAM_PROMPT = """\
You are creating an educational diagram for an 8th-grade {subject} lesson titled \
"{topic}".

Here is an excerpt from the lesson for context:
---
{excerpt}
---

Using matplotlib, write and run Python code that creates ONE clear, colorful, \
well-labeled diagram that visually explains the single most important concept in \
this lesson for a 13-year-old student.

Style requirements:
- Clean, modern, educational style — like a textbook figure, not a data chart
- Large, readable labels (font size 12+)
- Simple, friendly color palette (avoid neon or garish colors)
- White background
- Figure size 8x6 inches, dpi=150
- No legend clutter — label elements directly on the diagram where possible

Save the figure to a file named "diagram.png" using plt.savefig("diagram.png", \
bbox_inches="tight"). Do not display the plot. Then copy it to the output directory \
so it can be retrieved — run `cp diagram.png "$OUTPUT_DIR/diagram.png"` as a \
required final step. Confirm with `ls -lh "$OUTPUT_DIR/diagram.png"` that the file \
exists there before finishing.
"""


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug


def generate_diagram(topic: str, excerpt: str, subject: str) -> bytes | None:
    prompt = DIAGRAM_PROMPT.format(topic=topic, excerpt=excerpt, subject=subject)
    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
        tools=[{"type": "code_execution_20260120", "name": "code_execution"}],
    )

    file_id = None
    for block in response.content:
        if block.type != "bash_code_execution_tool_result":
            continue
        result = block.content
        if result.type != "bash_code_execution_result" or not result.content:
            continue
        for file_ref in result.content:
            if file_ref.type != "bash_code_execution_output":
                continue
            metadata = client.beta.files.retrieve_metadata(file_ref.file_id)
            if Path(metadata.filename).suffix.lower() in IMAGE_EXTS:
                file_id = file_ref.file_id

    if not file_id:
        return None

    downloaded = client.beta.files.download(file_id)
    return downloaded.read()


def embed_image(content: str, image_path: str, alt_text: str) -> str:
    if "![" in content:
        return content  # already illustrated
    marker = "## Core Concepts"
    image_md = f"\n\n![{alt_text}]({image_path})\n"
    if marker in content:
        return content.replace(marker, marker + image_md, 1)
    return content + image_md


def main():
    subject_name = sys.argv[1] if len(sys.argv) > 1 else "Chemistry"
    subject_slug = slugify(subject_name)
    static_dir = Path(__file__).parent / "static" / subject_slug
    static_dir.mkdir(parents=True, exist_ok=True)

    db = SessionLocal()
    lessons = (
        db.query(models.Lesson)
        .join(models.Topic)
        .join(models.Subject)
        .filter(models.Subject.name == subject_name)
        .order_by(models.Topic.order)
        .all()
    )

    total = len(lessons)
    print(f"Generating visuals for {total} {subject_name} lessons with Claude {MODEL}...\n")

    failed = []
    skipped = 0

    for i, lesson in enumerate(lessons, 1):
        if "![" in lesson.content:
            print(f"[{i}/{total}] {lesson.title} -- already has an image, skipping")
            skipped += 1
            continue

        print(f"[{i}/{total}] {lesson.title} ... ", end="", flush=True)
        slug = slugify(lesson.title)
        try:
            image_bytes = generate_diagram(lesson.title, lesson.content[:1200], subject_name)
            if not image_bytes:
                print("FAILED — no image file produced")
                failed.append(lesson.title)
                continue

            filename = f"{slug}.png"
            (static_dir / filename).write_bytes(image_bytes)

            web_path = f"/static/{subject_slug}/{filename}"
            lesson.content = embed_image(lesson.content, web_path, f"Diagram: {lesson.title}")
            db.commit()
            print(f"OK ({len(image_bytes)} bytes)")
        except Exception as e:
            db.rollback()
            failed.append(lesson.title)
            print(f"FAILED — {e}")

    db.close()

    print(f"\n{'=' * 50}")
    succeeded = total - skipped - len(failed)
    print(f"Done. {succeeded}/{total} lessons illustrated ({skipped} already done).")
    if failed:
        print(f"\nFailed ({len(failed)}):")
        for title in failed:
            print(f"  - {title}")


if __name__ == "__main__":
    main()
