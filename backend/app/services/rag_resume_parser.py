import PyPDF2
from docx import Document
from typing import Dict, Any
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json

from app.core.config import settings

class RAGResumeParser:
    def __init__(self):
        # Initialize LLM with config
        self.llm = OpenAI(
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Define prompt template
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
        
        # Build chain using LCEL (modern approach)
        self.chain = self.prompt | self.llm | StrOutputParser()

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
        elif mimetype.endswith("wordprocessingml.document"):
            return self.extract_text_from_docx(filepath)
        else:
            raise ValueError(f"Unsupported file type: {mimetype}")

    def parse_resume(self, filepath: str, mimetype: str) -> Dict[str, Any]:
        resume_text = self.extract_text_from_file(filepath, mimetype)
        
        # Invoke chain with LCEL
        llm_output = self.chain.invoke({"resume_text": resume_text})
        
        try:
            parsed_data = json.loads(llm_output)
        except Exception:
            parsed_data = {"raw_output": llm_output}
        
        parsed_data["raw_text"] = resume_text
        return parsed_data
