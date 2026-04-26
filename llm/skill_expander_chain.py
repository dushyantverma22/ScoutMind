# llm/skill_expander_chain.py

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import Dict, List


class SkillMap(BaseModel):
    skills: Dict[str, List[str]]


prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a recruiting expert.

For each skill, generate:
- synonyms
- abbreviations
- related tools

Return JSON:

{{
  "skills": {{
    "python": ["python", "py", "python3"]
  }}
}}
"""),

    ("user", """
Role: {role}
Skills: {skills}
""")
])


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


skill_chain = prompt | llm.with_structured_output(SkillMap, method="function_calling")
