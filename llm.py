import json
import os

import openai
from dotenv import load_dotenv

from data_models import Agent, Task

load_dotenv()


def generate_openai_answer(agent: Agent, task: Task) -> str:
    full_prompt = f"{agent.prompt}\n\nTask: {task.content}\n\nLibrary: {task.library.name} {task.library.version}\nLanguage: {task.library.language.name} {task.library.language.version}"

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.responses.create(
            model=agent.model.name,
            input=full_prompt,
        )

        return json.dumps(response.output_text, indent=2)

    except Exception as e:
        return f"Error generating answer using OpenAI API: {str(e)}"


def generate_answer(agent: Agent, task: Task) -> str:
    provider = agent.model.provider.lower()

    match provider:
        case "openai":
            return generate_openai_answer(agent, task)
        case _:
            raise ValueError(f"Unsupported model provider: {agent.model.provider}")
