import sys
import os
import asyncio
import json
import uuid
import logging

# Ensure backend/ is on path so imports like `app.*` resolve when running the script directly
HERE = os.path.dirname(os.path.dirname(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from sqlalchemy import select

from app.core.database import async_session
from app.services.resumeparser import ResumeParser, FileParseError
# Ensure related models are imported so SQLAlchemy mappers are configured
import app.models.candidate  # noqa: F401
from app.models.resume import Resume

logger = logging.getLogger("run_parse_test")
logging.basicConfig(level=logging.INFO)


async def main():
    base = os.path.dirname(os.path.dirname(__file__))  # backend/
    test_file = os.path.join(base, "test_resume.pdf")
    if not os.path.exists(test_file):
        print("Test resume not found:", test_file)
        return

    filename = os.path.basename(test_file)
    parser = ResumeParser()

    # Perform insert/find -> parse -> update within a single session to avoid asyncpg concurrency issues
    async with async_session() as session:
        # Try to find existing resume by filename
        try:
            result = await session.execute(select(Resume).where(Resume.filename == filename))
            resume = result.scalars().first()
        except Exception as e:
            logger.warning("Select failed (will attempt insert): %s", e)
            resume = None

        if not resume:
            resume_id = uuid.uuid4()
            resume = Resume(
                id=resume_id,
                candidate_id=None,
                filename=filename,
                file_path=test_file,
            )
            session.add(resume)
            try:
                await session.commit()
                await session.refresh(resume)
                print("Inserted resume record with id:", resume.id)
            except Exception as e:
                await session.rollback()
                logger.warning("Insert failed (might already exist): %s", e)
                # attempt to re-select
                result = await session.execute(select(Resume).where(Resume.filename == filename))
                resume = result.scalars().first()
                if not resume:
                    print("Could not create or find resume record; aborting")
                    return
        else:
            print("Found resume in DB with id:", resume.id)

        # Parse (do parsing between DB operations)
        try:
            parsed = parser.parse_resume(test_file, "application/pdf")
        except FileParseError as e:
            logger.exception("Parsing failed: %s", e)
            return
        except Exception as e:
            logger.exception("Unexpected parse error: %s", e)
            return

        # Prepare summary for output
        skills_list = parsed.get("skills") if isinstance(parsed.get("skills"), list) else []
        summary = {
            "id": str(resume.id),
            "filename": filename,
            "email": parsed.get("personal_info", {}).get("email"),
            "phone": parsed.get("personal_info", {}).get("phone"),
            "skills_count": len(skills_list),
            "experience_years": parsed.get("experience_years"),
        }
        print("Parse summary:")
        print(json.dumps(summary, indent=2))

        # Update resume row with parsed data
        resume.parsed_data = parsed
        resume.raw_text = parsed.get("raw_text")
        resume.skills = skills_list or None
        resume.experience_years = parsed.get("experience_years")

        session.add(resume)
        try:
            await session.commit()
            await session.refresh(resume)
            print("Updated resume record in DB. Parsed fields saved.")
        except Exception as e:
            await session.rollback()
            logger.exception("Failed to save parsed data to DB: %s", e)


if __name__ == '__main__':
    asyncio.run(main())
