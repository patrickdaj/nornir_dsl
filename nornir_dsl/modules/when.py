from functools import wraps
from typing import Callable, Union, List, Dict, Any
from nornir.core.task import Result


def when(
    conditions: Union[str, List[str]], pb_vars: Dict[str, Any]
) -> Callable[..., Any]:
    def decorator(wrapped) -> Callable[..., Any]:
        @wraps(wrapped)
        def wrapper(task: Callable[..., Any], **kwargs: Dict[str, Any]) -> Result:

            if pb_vars.get(task.host.name, None):
                host_vars = pb_vars[task.host.name]
            else:
                host_vars = {}

            if isinstance(conditions, str):
                test_conditions = [conditions]
            else:
                test_conditions = conditions

            test_parser = TestVisitor({
                'task': task,
                **host_vars
            })

            for condition in test_conditions:
                if not test_parser.safe_eval(condition):
                    return "Skipped"

            return wrapped(task, **kwargs)

        return wrapper

    return decorator
