import glob


def find_config_file(configs_dir: str, pattern: str) -> str:
    matches = sorted(glob.glob(f"{configs_dir}/{pattern}"))
    if not matches:
        raise FileNotFoundError(
            f"No config file matching pattern '{pattern}' found in '{configs_dir}'"
        )
    return matches[0]
