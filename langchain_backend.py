from langchain.prompts import PromptTemplate
from langchain_text_splitters import CharacterTextSplitter
import fitz  # PyMuPDF
from typing import List
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize the OpenAI LLM
llm = ChatOpenAI(model="gpt-4",
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0,
               )

class CandidateResult(BaseModel):
    candidate_name: str = Field(description="Candidate's full name as it appears in the resume")
    match_score: int = Field(ge=0, le=100, description="Percentage match between the resume and the job description/skills")
    shortlisted: bool = Field(description="True if match_score is above 65, otherwise False")
    highlights: str = Field(description="One-line summary of important things: years of experience, qualifications")
    risk_factor: str = Field(description="One-line risk factor, e.g. job changes within two years; 'None noted' if none")

class CandidateAnalysisBatch(BaseModel):
    candidates: List[CandidateResult] = Field(
        default_factory=list,
        description="One entry per distinct candidate resume found in the text; empty if none found",
    )

# Define the prompt template for ranking skills
prompt_template = PromptTemplate(
    input_variables=["job_description", "skills", "resume_text"],
    template="""
      You are a skilled and experienced ATS (Application Tracking System) with a deep understanding of the tech field, software engineering, data science, data analysis, and big data engineering.

      The resume text below may contain ONE candidate, MULTIPLE candidates concatenated together, or NO resume content at all.
      For each distinct candidate you can identify, evaluate them against the job description and skills and add one entry to `candidates` with:
        - candidate_name
        - match_score: percentage match (0-100), judged with high accuracy
        - shortlisted: true if match_score is above 65, otherwise false
        - highlights: one line covering years of experience and qualifications
        - risk_factor: one line noting risk factors such as job changes within two years ("None noted" if none)

      If the text contains no identifiable resume content, return an empty candidates list.

      Job Description:
      {job_description}

      Skills:
      {skills}

      Resume Text:
      {resume_text}
    """
)

structured_llm = llm.with_structured_output(CandidateAnalysisBatch, method="function_calling")
analysis_chain = prompt_template | structured_llm

def process_with_langchain(job_description: str, skills: str, pdf_files: List[bytes]) -> List[CandidateResult]:
    all_texts = []
    for file_bytes in pdf_files:
        pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
        pdf_text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            pdf_text += page.get_text()

        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0)
        docs = text_splitter.split_text(pdf_text)
        all_texts.extend(docs)

    max_tokens = 7500  # Keeping some buffer below the 8192 token limit
    combined_texts = []
    current_text = ""
    for doc in all_texts:
        if len(current_text) + len(doc) > max_tokens:
            combined_texts.append(current_text)
            current_text = doc
        else:
            current_text += doc

    if current_text:
        combined_texts.append(current_text)

    all_candidates: List[CandidateResult] = []
    for chunk in combined_texts:
        batch: CandidateAnalysisBatch = analysis_chain.invoke({
            "job_description": job_description,
            "skills": skills,
            "resume_text": chunk,
        })
        all_candidates.extend(batch.candidates)

    return all_candidates
