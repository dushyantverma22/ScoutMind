# llm/scoring_chain.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List


class CandidateScore(BaseModel):
    match_score: int
    matched_skills: List[str]
    missing_skills: List[str]
    explanation: str


prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an expert recruiter evaluating candidates.

Score how well the candidate matches the job description.

Return:
- match_score (0-100)
- matched_skills
- missing_skills
- explanation (2 lines)
"""),

    ("user", """
Job Description:
{jd}

Candidate:
{candidate}
""")
])


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


scoring_chain = prompt | llm.with_structured_output(CandidateScore)