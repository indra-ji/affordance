from data_models import Answer, Test


def safe_import(name, *args, **kwargs):
    blocked = {
        "os",
        "sys",
        "subprocess",
        "socket",
        "urllib",
        "requests",
    }
    if name in blocked:
        raise ImportError(f"Import of '{name}' is blocked")
    return __import__(name, *args, **kwargs)


def generate_result(answer: Answer, test: Test) -> bool:
    try:
        safe_builtins = dict(__builtins__)
        safe_builtins["__import__"] = safe_import

        namespace = {"__builtins__": safe_builtins}

        exec(answer.content, namespace)
        exec(test.content, namespace)
        return True
    except AssertionError as e:
        print(f"Test failed for task - {answer.task.name}: {e}")
        return False
    except Exception as e:
        print(f"Error generating result: {e}")
        return False
