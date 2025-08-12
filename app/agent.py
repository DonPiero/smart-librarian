from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import get_summary_by_title, search_relevant_books, language_filter

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7
)

tools = [get_summary_by_title, search_relevant_books]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful and friendly AI librarian. You can recommend books based on user interests and also have casual conversations.\n\n"
                "When the user seems to be looking for a book:\n"
                "1. Use the `search_relevant_books` tool to find a few matching titles and short summaries.\n"
                "2. Pick the most suitable book from the search results and explain why it's a good match.\n"
                "3. If you're confident in the title, automatically call the `get_summary_by_title` tool to provide the full summary — do not wait for user confirmation.\n\n"
                "Only call the tools when it is appropriate and you're confident.\n"
                "Only recommend books when you're confident that the user is looking for a recommendation.\n"
                "If you're unsure, politely ask for clarification or continue the conversation.\n"
                "If you don't have a match, admit that you don't know. Only suggest a book if it was found in the library search results.\n"
                "Do NOT invent titles or recommend books that are not found in the library's collection.\n"
                "You must only recommend books that appear in the search results. Never mention books that are not present in the library's data.\n"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=ConversationBufferMemory(return_messages=True)
)

def chat_with_agent(query: str) -> str:
    query = query.strip()
    if language_filter(query):
        return "Please use a respectful language. After you calm down, we may resume our conversation."
    response = executor.invoke({"input": query})
    return response["output"].strip()


if __name__ == "__main__":
    print("Smart Librarian – type 'exit' or 'quit' to quit.")

    while True:
        q = input("> ")
        if q.lower() in {"exit", "quit"}:
            print("Have a nice day and happy reading!")
            break

        if not q.strip():
            continue

        print("\n", chat_with_agent(q))