import asyncio
import os
import uuid
from typing import List

from sqlalchemy import select

from app.core.database import async_session
from app.models.jobs import Job
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.models.applications import Application
from app.models.screening_results import ScreeningResult
from app.services.embeddings import get_embedding, vector_store


DEMO_UPLOADS_DIR = "./uploads"


def ensure_demo_file(filename: str, content: str) -> str:
    os.makedirs(DEMO_UPLOADS_DIR, exist_ok=True)
    path = os.path.join(DEMO_UPLOADS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


async def seed_jobs(session) -> List[Job]:
    existing = (await session.execute(select(Job))).scalars().all()
    if existing:
        return existing

    jobs = [
        Job(
            id=uuid.uuid4(),
            title="Senior Python/FastAPI Engineer",
            description="Build and scale APIs. Collaborate with product and infra.",
            requirements="Python, FastAPI, SQL, Docker, AWS, CI/CD",
            location="Remote",
            salary_min=120000,
            salary_max=160000,
            status="active",
        ),
        Job(
            id=uuid.uuid4(),
            title="Frontend Engineer (React + TypeScript)",
            description="Own UI components and performance.",
            requirements="React, TypeScript, Tailwind, Testing, Accessibility",
            location="Remote",
            salary_min=100000,
            salary_max=140000,
            status="active",
        ),
    ]
    for j in jobs:
        session.add(j)
    await session.commit()
    for j in jobs:
        text = f"{j.title}\n{j.description}\n{j.requirements}"
        vec = get_embedding(text[:5000])
        vector_store.upsert("jobs", [(str(j.id), vec, {"title": j.title})])
    return jobs


async def seed_candidates_and_resumes(session) -> List[Candidate]:
    existing = (await session.execute(select(Candidate))).scalars().all()
    if existing:
        return existing

    candidates = [
        Candidate(id=uuid.uuid4(), name="Alice Johnson", email="alice@example.com"),
        Candidate(id=uuid.uuid4(), name="Bob Smith", email="bob@example.com"),
    ]
    for c in candidates:
        session.add(c)
    await session.commit()

    # Create simple text resumes and embed
    resumes_payload = [
        (
            candidates[0],
            "alice_resume.txt",
            "Alice Johnson\nExperience: 5 years Python, FastAPI, SQL, Docker, AWS.\nEducation: B.S. Computer Science",
            ["Python", "FastAPI", "SQL", "Docker", "AWS"],
            5,
            "B.S. Computer Science",
        ),
        (
            candidates[1],
            "bob_resume.txt",
            "Bob Smith\nExperience: 4 years React, TypeScript, Tailwind, Testing.\nEducation: B.S. Software Engineering",
            ["React", "TypeScript", "Tailwind"],
            4,
            "B.S. Software Engineering",
        ),
    ]

    for cand, fname, content, skills, years, edu in resumes_payload:
        path = ensure_demo_file(fname, content)
        r = Resume(
            id=uuid.uuid4(),
            candidate_id=cand.id,
            filename=fname,
            file_path=path,
            parsed_data={
                "raw_text": content,
                "skills": skills,
                "experience_years": years,
                "education": [{"degree": edu}],
            },
            raw_text=content,
            skills=skills,
            experience_years=years,
            education_level=edu,
        )
        session.add(r)
        await session.commit()
        emb_text = content + "\n" + " ".join(skills)
        vec = get_embedding(emb_text[:5000])
        vector_store.upsert("resumes", [(str(r.id), vec, {"filename": fname, "candidate_id": str(cand.id)})])

    return candidates


async def main():
    async with async_session() as session:
        jobs = await seed_jobs(session)
        candidates = await seed_candidates_and_resumes(session)
        print(f"Seeded {len(jobs)} jobs and {len(candidates)} candidates/resumes.")


if __name__ == "__main__":
    asyncio.run(main())


