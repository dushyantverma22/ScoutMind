# llm/summary_chain.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel


class ConversationSummary(BaseModel):
    summary: str


prompt = ChatPromptTemplate.from_messages([
    ("system", "Summarize recruiter-candidate conversation briefly."),
    ("user", """
Conversation:
{conversation}

Focus on:
- interest level
- concerns
""")
])


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

summary_chain = prompt | llm.with_structured_output(ConversationSummary)