import datetime
import glob
import json
import re
from typing import Type, get_args

from data_models import ValidDataModel, ValidDataModelType


def find_config_file(configs_dir: str, pattern: str) -> str:
    matches = sorted(glob.glob(f"{configs_dir}/{pattern}"))
    first_match = matches[0]
    return first_match


def serialize_data_model(output_path: str, data_model: ValidDataModel) -> None:
    valid_data_models = get_args(ValidDataModel)

    if type(data_model) in valid_data_models:
        json_output = data_model.model_dump_json(indent=2)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_output)
    else:
        raise ValueError(
            f"Invalid data model type: {data_model.__name__}. "
            f"Must be one of: {[cls.__name__ for cls in valid_data_models]}"
        )


def deserialize_data_model(
    input_path: str, data_model_type: Type[ValidDataModelType]
) -> ValidDataModel:
    valid_data_model_types = get_args(ValidDataModel)

    if data_model_type in valid_data_model_types:
        with open(input_path, "r", encoding="utf-8") as f:
            json_data = f.read()
        return data_model_type.model_validate_json(json_data)
    else:
        raise ValueError(
            f"Invalid data model type: {data_model_type.__name__}. "
            f"Must be one of: {[cls.__name__ for cls in valid_data_model_types]}"
        )


def deserialize_dict(input_path: str) -> dict:
    with open(input_path, "r", encoding="utf-8") as f:
        json_data = f.read()
    return json.loads(json_data)


def clean_code(text: str) -> str:
    text = re.sub(r"```[ \t]*[A-Za-z0-9_+\-]*", "", text)
    text = re.sub(r"```", "", text)
    return text


def generate_evaluation_output_path(
    evaluation_name: str, model_name: str, eval_dir: str = "evals"
) -> str:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_eval_name = evaluation_name.replace(" ", "_")
    return f"{eval_dir}/{safe_eval_name}_{model_name}_{timestamp}.json"
