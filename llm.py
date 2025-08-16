import os

import openai
from dotenv import load_dotenv

from data_models import Agent, Task
from utils import clean_code

load_dotenv()


def generate_openai_answer(agent: Agent, task: Task) -> str:
    full_prompt = (
        f"{agent.prompt}\n\n"
        f"Task: {task.content}\n\n"
        f"Library: {task.library.name} {task.library.version}\n"
        f"Language: {task.library.language.name} {task.library.language.version}"
    )

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.responses.create(
            model=agent.model.name,
            input=full_prompt,
        )

        output = response.output_text
        output = clean_code(output)

        return output

    except Exception as e:
        raise RuntimeError(f"Error generating answer using OpenAI API: {str(e)}") from e


def generate_answer(agent: Agent, task: Task) -> str:
    provider = agent.model.provider.lower()

    match provider:
        case "openai":
            return generate_openai_answer(agent, task)
        case _:
            raise ValueError(f"Unsupported model provider: {agent.model.provider}")
