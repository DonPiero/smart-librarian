from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from app.config.classes import ModelConfig, PromptConfig
from app.services.openai_client import build_prompt, build_llm
from app.utils.tools import get_summary_by_title, search_relevant_books
from app.utils.validators import language_filter


def create_agent(
    model: ModelConfig,
    prompt: PromptConfig
):
    try:
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
            memory=memory
        )

        def chat_with_agent(query: str) -> str:
            try:
                if not query or not query.strip():
                    raise ValueError(
                        "Providing an empty input is not supported.")

                if language_filter(query):
                    return ("Please use a respectful language. "
                            "After you calm down, "
                            "we may resume our conversation.")

                user_input = query.strip()

                response = executor.invoke({"input": user_input})
                return response["output"].strip()

            except Exception as chatError:
                return f"Error appeared at conversation level: {chatError}."

        return chat_with_agent

    except Exception as factoryError:
        def dead_chatbot(_: str, err=factoryError):
            return f"Error appeared at factory level: {err}."
        return dead_chatbot
