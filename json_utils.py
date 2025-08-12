import json
import re

from data_models import BaseEntity


def serialize_data_model(output_path: str, data_model: type[BaseEntity]) -> None:
    json_output = data_model.model_dump_json(indent=2)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json_output)


def deserialize_data_model(
    input_path: str, model_class: type[BaseEntity]
) -> type[BaseEntity]:
    with open(input_path, "r", encoding="utf-8") as f:
        json_data = f.read()
    return model_class.model_validate_json(json_data)


def deserialize_dict(input_path: str) -> dict:
    with open(input_path, "r", encoding="utf-8") as f:
        json_data = f.read()
    return json.loads(json_data)


def clean_code(text: str) -> str:
    return re.sub(r"```[ \t]*[A-Za-z0-9_+\-]*", "", text)
