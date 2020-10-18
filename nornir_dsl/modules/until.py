from functools import wraps
from typing import Callable, Union, List, Dict, Any
import time
from nornir.core.task import Result
from nornir_dsl.utils.safe_evals import TestVisitor

def until(
    pb_vars: Dict[str, Any],
    conditions: Union[str, List[str]],
    initial_delay: int,
    retries: int,
    delay: int,
    reset_conn: bool,
) -> Callable[..., Any]:
    def decorator(wrapped: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(wrapped)
        def wrapper(task, **kwargs: Dict[str, Any]) -> Result:

            failed_conditions = False

            if pb_vars.get(task.host.name, None):
                host_vars = pb_vars[task.host.name]
            else:
                host_vars = {}

            if isinstance(conditions, str):
                test_conditions = [conditions]
            else:
                test_conditions = conditions

            if initial_delay:
                time.sleep(initial_delay)

            for retry in retries:
                result = wrapped(task, **kwargs)
                test_parser = TestVisitor({
                    'result': result,
                    **host_vars
                })

                for condition in test_conditions:
                    if not test_parser.safe_eval(condition):
                        failed_conditions = True

                if failed_conditions:
                    time.sleep(delay)

                if reset_conn:
                    task.host.connection.close()

            if failed_conditions:
                raise Exception("Task never completed successfully with retries")

            return result

        return wrapper

    return decorator
