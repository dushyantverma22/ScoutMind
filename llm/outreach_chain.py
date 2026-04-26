# llm/outreach_chain.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel


# -------------------------------
# Candidate Reply
# -------------------------------
class CandidateReply(BaseModel):
    reply: str


reply_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a job candidate.

Respond naturally to a recruiter message.
Some candidates are:
- actively looking
- passive
- not interested
"""),

    ("user", """
Candidate:
{candidate}

Message:
{message}
""")
])


# -------------------------------
# Interest Score
# -------------------------------
class InterestScore(BaseModel):
    interest_score: int
    explanation: str


score_prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a recruiter.

Based on the conversation, give:
- interest_score (0-100)
- explanation

0-30 → Not interested  
30-60 → Passive  
60-100 → Interested  
"""),

    ("user", """
Conversation:
{conversation}
""")
])


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

reply_chain = reply_prompt | llm.with_structured_output(CandidateReply)
score_chain = score_prompt | llm.with_structured_output(InterestScore)