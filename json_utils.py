from data_models import BaseEntity


def serialize_data_model(data_model: type[BaseEntity], output_path: str) -> None:
    json_output = data_model.model_dump_json(indent=2)

    with open(output_path, "w") as f:
        f.write(json_output)


def deserialize_data_model(
    input_path: str, model_class: type[BaseEntity]
) -> type[BaseEntity]:
    with open(input_path, "r") as f:
        json_data = f.read()
    return model_class.model_validate_json(json_data)
