from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import CharacterTextSplitter
import fitz  # PyMuPDF
from typing import List
from langchain_openai import ChatOpenAI

# Initialize the OpenAI LLM
llm = ChatOpenAI(model="gpt-4",
                openai_api_key="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",
                temperature=0 ,
                streaming=True,
               )

# Define the prompt template for ranking skills
prompt_template = PromptTemplate(
    input_variables=["job_description", "skills", "resume_text"],
    template="""
      Given the following job description, skills, and resume, do the following:
      1. Act like a skilled or very experienced ATS (Application Tracking System) with a deep understanding of the tech field, software engineering, data science, data analysis, and big data engineering. Evaluate the resume based on the given job description and skills.
      2. Assign a percentage matching score based on the job description and skills with very high accuracy.
      3. Display a 'Yes' message if the resume score is above 65%, otherwise display a 'No' message.
      4. Search within the resume for important things about the candidate, such as years of experience and qualifications.
      5. Search within the resume for risk factors, such as job changes within two years.

      Job Description:
      {job_description}

      Skills:
      {skills}

      Resume:
      {resume_text}

    So my final output should look like:
        - Candidate's name
        - Percentage matching score
        - Based on percentage: Yes/No
        - Important things in 1 line
        - Risk factor
    """
)

def process_with_langchain(job_description: str, skills: str, pdf_files: List[bytes]):
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

    results = []
    for chunk in combined_texts:
        chain = LLMChain(prompt=prompt_template, llm=llm, output_parser=StrOutputParser())
        result = chain.invoke(input={"job_description": job_description, "skills": skills, "resume_text": chunk})
        result_str = result["text"] if isinstance(result, dict) and "text" in result else str(result)
        results.append(result_str)

    aggregated_result = "\n".join(results)
    return {"result": aggregated_result}