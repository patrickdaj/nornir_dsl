from functools import wraps
from typing import Callable, Union, List, Dict, Any
from nornir.core.task import Result


def test(
    pb_vars: Dict[str, Any],
    conditions: Union[str, List[str]],
    fail_task: bool
) -> Callable[..., Any]:
    def decorator(wrapped) -> Callable[..., Any]:
        @wraps(wrapped)
        def wrapper(task: Callable[..., Any], **kwargs: Dict[str, Any]) -> Result:

            import ipdb; ipdb.set_trace()
            result = wrapped(task, **kwargs)

            if pb_vars.get(task.host.name, None):
                for attr in pb_vars[task.host.name].keys():
                    locals()[attr] = pb_vars[task.host.name][attr]

            if isinstance(conditions, str):
                test_conditions = [conditions]
            else:
                test_conditions = conditions

            for condition in test_conditions:
                if not eval(condition):
                    result.failed = True

            return result

        return wrapper

    return decorator
