from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from app.config.classes import ModelConfig, PromptConfig
from app.services.openai_client import build_prompt, build_llm
from app.services.agent_tools import get_summary_by_title, search_relevant_books
from app.utils.validators import language_filter


def create_agent(
    model: ModelConfig,
    prompt: PromptConfig
):
    try:
        if not (0.0 <= float(model.temperature) <= 2.0):
            raise ValueError(
                "Temperature must be between 0.0 and 2.0")
        if not (0.0 <= float(model.top_p) <= 1.0):
            raise ValueError(
                "Top_p must be in the interval [0.0, 1.0]")
        if not (-2.0 <= float(model.presence_penalty) <= 2.0):
            raise ValueError(
                "Presence_penalty must be between -2.0 and 2.0")
        if not (-2.0 <= float(model.frequency_penalty) <= 2.0):
            raise ValueError(
                "Frequency_penalty must be between -2.0 and 2.0.")
        if not (isinstance(model.max_tokens, int) and model.max_tokens > 0):
            raise ValueError(
                "Max_tokens must be a positive integer.")

        prompt_template = build_prompt(prompt)
        llm = build_llm(model)
        tools = [get_summary_by_title, search_relevant_books]

        agent = create_openai_tools_agent(
            llm=llm,
            tools=tools,
            prompt=prompt_template
        )

        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True
        )

        def chat_with_agent(query: str) -> str:
            try:
                if not query or not query.strip():
                    raise ValueError(
                        "Providing an empty input is not supported.")

                if language_filter(query):
                    return "Please use a respectful language. After you calm down, we may resume our conversation."

                user_input = query.strip()

                response = executor.invoke({"input": user_input})
                return response["output"].strip()

            except Exception as chatError:
                return f"This error appeared at conversation level: {chatError}."

        return chat_with_agent

    except Exception as factoryError:
        def dead_chatbot(_: str, err=factoryError):
            return f"This error appeared at factory level: {err}."
        return dead_chatbot

if __name__ == "__main__":
    model_cfg = ModelConfig()
    prompt_cfg = PromptConfig()

    chat = create_agent(model_cfg, prompt_cfg)

    print("My name is ProjectLens and I am your friendly insurance assistant."
          " Type 'exit' to quit.\n")

    while True:
        msg = input("You: ")
        if msg.lower() == "exit":
            print("Goodbye!")
            break
        result = chat(msg)
        print("\nProjectLens:", result)
