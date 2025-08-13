import datetime
import glob
import json
import re

from data_models import BaseEntity


def find_config_file(configs_dir: str, pattern: str) -> str:
    matches = sorted(glob.glob(f"{configs_dir}/{pattern}"))
    if not matches:
        raise FileNotFoundError(
            f"No config file matching pattern '{pattern}' found in '{configs_dir}'"
        )
    return matches[0]


def serialize_data_model(output_path: str, data_model: type[BaseEntity]) -> None:
    json_output = data_model.model_dump_json(indent=2)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json_output)


def deserialize_data_model(
    input_path: str, data_model: type[BaseEntity]
) -> type[BaseEntity]:
    with open(input_path, "r", encoding="utf-8") as f:
        json_data = f.read()
    return data_model.model_validate_json(json_data)


def deserialize_dict(input_path: str) -> dict:
    with open(input_path, "r", encoding="utf-8") as f:
        json_data = f.read()
    return json.loads(json_data)


def clean_code(text: str) -> str:
    return re.sub(r"```[ \t]*[A-Za-z0-9_+\-]*", "", text)


def generate_evaluation_output_path(
    evaluation_name: str, model_name: str, eval_dir: str = "evals"
) -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_eval_name = evaluation_name.replace(" ", "_")
    return f"{eval_dir}/{safe_eval_name}_{model_name}_{timestamp}.json"
