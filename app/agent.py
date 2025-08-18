from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_openai_functions_agent
from tools import get_summary_by_title, search_relevant_books, language_filter

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3
)

tools = [get_summary_by_title, search_relevant_books]

prompt = ChatPromptTemplate.from_messages([
    ("system", """ 
    You are Smart Librarian — a concise, helpful assistant that recommends and summarizes books strictly from our internal library via tools.

- Never recommend or discuss a book unless it was returned by the `search_relevant_books` tool.  
- If a title is mentioned by the user, always verify it using `get_summary_by_title`.

- `search_relevant_books(query)`: Finds titles by topic or genre. Returns a list of titles that is MANDATORY to be presented to the user.
- `get_summary_by_title(title)`: Returns the full summary for a specific book.

- When asked for a topic or genre:
    1. Call `search_relevant_books`.
    2. If no results → say: "I couldn’t find any titles in our library for that. Want to try another topic?"
    3. If results → you MUST ALWAYS do the following in this exact order:
        - Before giving any recommendation, you NEED to show the entire list of titles returned by the tool to the user. NEVER skip the list and say that those are the best matches".
        - Only then call `get_summary_by_title` for the first title, present it to the user and explain why its the best match.
    
- After you recommend a book and the user asks for another recommendation on the same topic:
    1. Look back at the most recent list.
    2. Pick the next unrecommended title and show its summary.
    3. If none left → say: “I’ve reached the end of the list. Want me to try a related genre?”

- If user asks about a specific title, call `get_summary_by_title`.  
- If not found → say: “That title isn’t in our library listings.”

- Be brief, warm, and direct.  
- After you use the search_relevant_books tool, ABSOLUTELY ALWAYS present the list of titles to the user before recommending any book.
- You must always call search_relevant_books first for topic/genre requests, even if you know a title.
- Do not guess, invent titles, or recommend books from outside the library.  
- If the user asks for “more details” or “full summary”, re-call `get_summary_by_title`."""
     ),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])


agent = create_openai_functions_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory
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