import streamlit as st
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import CharacterTextSplitter
import io
import fitz  # PyMuPDF

# Initialize the OpenAI LLM
llm = ChatOpenAI(model="gpt-4", openai_api_key="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",temperature=0)

# Define the prompt template for ranking skills
prompt_template = PromptTemplate(
    input_variables=["job_description", "skills", "resume_text"],
    template="""
      Given the following job description, skills, and resume, do the following:
      1. Act like a skilled or very experienced ATS (Application Tracking System) with a deep understanding of the tech field, software engineering, data science, data analysis, and big data engineering. Evaluate the resume based on the given job description and skills.
      2. Assign a percentage matching score based on the job description and skills with very high accuracy.
      3. Display a 'Yes' message if the resume score is above 65%, otherwise display a 'No' message.
      4. search within the resume for important thing about the candidate, such as  years of experience and  qualification 
      5. search within the resume for risk factors, such as job changes within two years.

      Job Description:
      {job_description}

      Skills:
      {skills}

      Resume:
      {resume_text}


    So my final output should look like 
        candidate's name 
        -percentage matching score
        -based on percentage yes/no
        -important things in 1 lines 
        -risk factor

    
    """
)

# Streamlit UI
st.title("Resume Analyzer")

# Job Description input
job_description = st.text_area("Job Description", height=200)

# Skills input
skills = st.text_area("Skills", height=200)

# Resume upload
uploaded_files = st.file_uploader("Upload your resume(s) (PDF)", type="pdf", accept_multiple_files=True)

if st.button("Analyze Resume"):
    if job_description and skills and uploaded_files:
        all_texts = []
        for uploaded_file in uploaded_files:
            # Read file content
            file_bytes = uploaded_file.read()
            
            # Load and process the PDF file
            pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
            pdf_text = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                pdf_text += page.get_text()

            text_splitter = CharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=0
            )
            docs = text_splitter.split_text(pdf_text)
            all_texts.extend(docs)

        # Ensure combined_text stays within token limits
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
        
        # Process each chunk individually
        results = []
        for chunk in combined_texts:
            chain = prompt_template | llm | StrOutputParser()
            result = chain.invoke(input={"job_description": job_description, "skills": skills, "resume_text": chunk})
            results.append(result)
        
        # Aggregate results
        aggregated_result = "\n".join(results)

        # Display results
        st.subheader("Analysis Result")
        st.write(aggregated_result)
    else:
        st.error("Please provide the job description, skills, and at least one resume PDF.")
