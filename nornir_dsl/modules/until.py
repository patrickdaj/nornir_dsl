from functools import wraps
from typing import Callable, Union, List, Dict, Any
import time
from nornir.core.task import Result


def until(
    pb_vars: Dict[str, Any], 
    conditions: Union[str, List[str]], 
    initial_delay: int, 
    retries: int,
    delay: int,
    reset_conn: bool
) -> Callable[..., Any]:
    def decorator(wrapped: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(wrapped)
        def wrapper(task, **kwargs: Dict[str, Any]) -> Result:

            failed_conditions = False

            if pb_vars.get(task.host.name, None):
                for attr in pb_vars[task.host.name].keys():
                    locals()[attr] = pb_vars[task.host.name][attr]

            if isinstance(conditions, str):
                test_conditions = [conditions]
            else:
                test_conditions = conditions

            if initial_delay:
                time.sleep(initial_delay)

            for retry in retries:
                result = wrapped(task, **kwargs)

                for condition in test_conditions:
                    if not eval(condition):
                        failed_conditions = True

                if failed_conditions:
                    time.sleep(delay)

                if reset_conn:
                    task.host.connection.close()

            return result

        return wrapper

    return decorator
