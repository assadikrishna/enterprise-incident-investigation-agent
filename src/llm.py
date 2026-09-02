from __future__ import annotations

import os
import time

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")

if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY is not set. "
        "Add it to a .env file in the project root."
    )

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "X-OpenRouter-Title": "Enterprise Incident Investigation Agent",
    },
)


def generate(
    prompt: str,
    max_attempts: int = 3,
    retry_delay_seconds: float = 2.0,
) -> str:
    """Send a prompt to OpenRouter and return a non-empty response."""
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    last_error = "Unknown OpenRouter failure."

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0,
                timeout=30.0,
            )

            if not response.choices:
                last_error = "OpenRouter returned no response choices."
            else:
                content = response.choices[0].message.content

                if content and content.strip():
                    return content.strip()

                last_error = "OpenRouter returned an empty response."

        except AuthenticationError as exc:
            raise RuntimeError(
                "OpenRouter authentication failed. Check OPENROUTER_API_KEY."
            ) from exc

        except RateLimitError as exc:
            last_error = "OpenRouter rate limit reached."

        except APIConnectionError as exc:
            last_error = "Could not connect to OpenRouter."

        except APITimeoutError as exc:
            last_error = "OpenRouter request timed out."

        except APIStatusError as exc:
            last_error = (
                f"OpenRouter returned HTTP {exc.status_code}: {exc.message}"
            )

        if attempt < max_attempts:
            print(
                f"{last_error} "
                f"Retrying in {retry_delay_seconds} seconds "
                f"({attempt}/{max_attempts})..."
            )
            time.sleep(retry_delay_seconds)

    raise RuntimeError(
        f"{last_error} Failed after {max_attempts} attempts."
    )