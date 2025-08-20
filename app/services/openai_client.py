from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from app.config.classes import PromptConfig, ModelConfig


def build_prompt(prompt_config: PromptConfig) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", prompt_config.instructions),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ]
    )


def build_llm(model_config: ModelConfig) -> ChatOpenAI:
    return ChatOpenAI(
        model=model_config.model,
        temperature=model_config.temperature,
        max_tokens=model_config.max_tokens,
        top_p=model_config.top_p,
        presence_penalty=model_config.presence_penalty,
        frequency_penalty=model_config.frequency_penalty,
        api_key=model_config.api_key,
        timeout=60.0,  # Set a timeout to avoid long waits
        max_retries=2  # Retry up to max_retries times in case of errors
    )
