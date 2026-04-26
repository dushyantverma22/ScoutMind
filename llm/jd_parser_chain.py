# llm/jd_parser_chain.py

from pydantic import BaseModel
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


# -------------------------------
# Output Schema
# -------------------------------
class JDStructured(BaseModel):
    role: str
    location: str
    experience_years: int
    required_skills: List[str]
    preferred_skills: List[str]
    domain: str
    seniority: str


# -------------------------------
# Prompt
# -------------------------------
jd_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an expert recruiter who extracts structured information from messy job descriptions.

Return clean structured JSON only.
"""),

    ("user", """
Extract the following from this Job Description:

- role
- location
- experience_years (number)
- required_skills (list)
- preferred_skills (list)
- domain (industry/domain)
- seniority (junior/mid/senior)

Job Description:
{jd}
""")
])


# -------------------------------
# LLM
# -------------------------------
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# -------------------------------
# Chain
# -------------------------------
jd_chain = jd_prompt | llm.with_structured_output(JDStructured)