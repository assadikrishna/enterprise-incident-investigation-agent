import os
import time
from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, RateLimitError
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


load_dotenv()


def generate_with_langchain(prompt: str) -> str:
    model = ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
    )

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("human", "{investigation_prompt}"),
        ]
    )

    chain = prompt_template | model

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        try:
            response = chain.invoke(
                {"investigation_prompt": prompt}
            )
            break

        except (APIConnectionError, APIStatusError, RateLimitError) as exc:
            if attempt == max_attempts:
                raise

            print(
                f"OpenRouter request failed: {exc}. "
                f"Retrying ({attempt}/{max_attempts})..."
            )
            time.sleep(2)

        except ValueError as exc:
            # OpenRouter may return an upstream provider error
            # that LangChain surfaces as ValueError.
            error_text = str(exc)

            if (
                "provider_overloaded" not in error_text
                and "temporarily overloaded" not in error_text
            ):
                raise

            if attempt == max_attempts:
                raise

            print(
                "OpenRouter provider temporarily overloaded. "
                f"Retrying in 2 seconds ({attempt}/{max_attempts})..."
            )
            time.sleep(2)

    if not isinstance(response.content, str):
        raise ValueError("Expected a text response from OpenRouter.")

    return response.content