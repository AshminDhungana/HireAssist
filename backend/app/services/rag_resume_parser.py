import PyPDF2
from docx import Document
from typing import Dict, Any
import json
import time
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class RAGResumeParser:
    def __init__(self):
        # Defer LLM/chain creation until needed and ensure API key present
        self.llm = None
        self.chain = None
        self._ensure_llm()

    def _ensure_llm(self):
        # Guard: if OPENAI_API_KEY not set, avoid initializing LLM
        if not getattr(settings, "OPENAI_API_KEY", None):
            logger.warning("OPENAI_API_KEY not set — RAG parser will not call LLM")
            return

        # Import lazily to avoid hard dependency at import time
        try:
            from langchain_openai import OpenAI
            from langchain_core.prompts import PromptTemplate
            from langchain_core.output_parsers import StrOutputParser
        except Exception:
            logger.exception("LangChain/OpenAI imports failed — RAG unavailable")
            return

        self.llm = OpenAI(temperature=0, openai_api_key=settings.OPENAI_API_KEY)

        self.prompt = PromptTemplate(
            input_variables=["resume_text"],
            template=(
                "Given the following resume text, extract and output a valid compact JSON including:"
                "\n- contact_info (email, phone)"
                "\n- skills (as a list)"
                "\n- education (as a list)"
                "\n- experience (as a list with company, title, dates)"
                "\nResume:\n{resume_text}\n"
                "Format output JSON as:"
                '{"contact_info": ..., "skills": [...], "education": [...], "experience": [...]}'
            )
        )

        try:
            self.chain = self.prompt | self.llm | StrOutputParser()
        except Exception:
            # If chain composition fails, leave chain as None
            logger.exception("Failed to build RAG chain")

    def extract_text_from_pdf(self, filepath: str) -> str:
        text = ""
        with open(filepath, "rb") as file:
            pdfreader = PyPDF2.PdfReader(file)
            for page in pdfreader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        return text

    def extract_text_from_docx(self, filepath: str) -> str:
        doc = Document(filepath)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)

    def extract_text_from_file(self, filepath: str, mimetype: str) -> str:
        if mimetype == "application/pdf":
            return self.extract_text_from_pdf(filepath)
        elif mimetype.endswith("wordprocessingml.document") or filepath.lower().endswith('.docx'):
            return self.extract_text_from_docx(filepath)
        else:
            raise ValueError(f"Unsupported file type: {mimetype}")

    def parse_resume(self, filepath: str, mimetype: str) -> Dict[str, Any]:
        resume_text = self.extract_text_from_file(filepath, mimetype)

        # If no LLM available, return raw_text only and mark raw_output
        if not self.chain:
            logger.info("RAG chain not available; returning raw text only")
            return {"raw_text": resume_text, "raw_output": None}

        # Call LLM with retries and exponential backoff
        attempts = 3
        backoff = 1
        last_exc = None
        for attempt in range(attempts):
            try:
                llm_output = self.chain.invoke({"resume_text": resume_text})
                try:
                    parsed_data = json.loads(llm_output)
                except Exception:
                    parsed_data = {"raw_output": llm_output}

                parsed_data["raw_text"] = resume_text
                return parsed_data
            except Exception as e:
                last_exc = e
                logger.exception("RAG parser attempt %s failed: %s", attempt + 1, e)
                time.sleep(backoff)
                backoff *= 2

        logger.error("RAG parser failed after %s attempts: %s", attempts, last_exc)
        # On repeated failure, return raw text and an error field
        return {"raw_text": resume_text, "raw_output": None, "error": str(last_exc)}
