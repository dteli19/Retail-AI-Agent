import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from tools import inspect_data, query_data, generate_insight
from prompts import SYSTEM_PROMPT

load_dotenv()

REACT_TEMPLATE = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

prompt = PromptTemplate.from_template(REACT_TEMPLATE)


def create_agent():
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.1-8b-instant",
        temperature=0
    )

    tools = [inspect_data, query_data, generate_insight]

    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=15,
        handle_parsing_errors=True
    )

    return agent_executor


def run_agent(question: str) -> str:
    import time
    agent_executor = create_agent()

    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print(f"{'='*60}\n")

    for attempt in range(3):
        try:
            result = agent_executor.invoke({
                "input": f"{SYSTEM_PROMPT}\n\n{question}"
            })
            return result['output']
        except Exception as e:
            if 'rate_limit' in str(e).lower() or '429' in str(e):
                print(f"Rate limit hit, waiting 30 seconds... (attempt {attempt+1}/3)")
                time.sleep(30)
            else:
                return f"Error: {str(e)}"
    return "Could not complete due to rate limits. Please try again in a minute."


if __name__ == '__main__':
    questions = [
        "Which customer segments have the most customers?",
        "What are the top performing product categories by revenue?",
        "Which promotions are giving the best ROI? Show me the top individual promotions ranked by ROI."
    ]

    import time
    for question in questions:
        answer = run_agent(question)
        print(f"\nFINAL ANSWER:\n{answer}")
        print("\n" + "="*60 + "\n")
        time.sleep(30)