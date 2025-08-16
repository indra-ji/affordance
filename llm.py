import os

import openai
from dotenv import load_dotenv
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from data_models import Agent, Task
from utils import clean_code

load_dotenv()


@retry(
    reraise=True,
    stop=stop_after_attempt(10),
    wait=wait_exponential(multiplier=1, min=1, max=256),
    retry=retry_if_exception_type(openai.RateLimitError),
)
async def generate_openai_answer(agent: Agent, task: Task) -> str:
    full_prompt = (
        f"{agent.prompt}\n\n"
        f"Task: {task.content}\n\n"
        f"Library: {task.library.name} {task.library.version}\n"
        f"Language: {task.library.language.name} {task.library.language.version}"
    )

    client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        response = await client.responses.create(
            model=agent.model.name,
            input=full_prompt,
        )

        output = response.output_text
        output = clean_code(output)

        return output
    except openai.RateLimitError:
        raise
    except Exception as e:
        raise RuntimeError(f"Error generating answer using OpenAI API: {str(e)}") from e


async def generate_answer(agent: Agent, task: Task) -> str:
    provider = agent.model.provider.lower()

    match provider:
        case "openai":
            return await generate_openai_answer(agent, task)
        case _:
            raise ValueError(f"Unsupported model provider: {agent.model.provider}")
