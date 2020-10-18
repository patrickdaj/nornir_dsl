from functools import wraps
from typing import Callable, Union, List, Dict, Any
from nornir.core.task import Result
from nornir_dsl.utils.safe_evals import TestVisitor

def test(
    pb_vars: Dict[str, Any], conditions: Union[str, List[str]], fail_task: bool
) -> Callable[..., Any]:
    def decorator(wrapped) -> Callable[..., Any]:
        @wraps(wrapped)
        def wrapper(task: Callable[..., Any], **kwargs: Dict[str, Any]) -> Result:

            result = wrapped(task, **kwargs)

            if pb_vars.get(task.host.name, None):
                host_vars = pb_vars[task.host.name]
            else:
                host_vars = {}

            if isinstance(conditions, str):
                test_conditions = [conditions]
            else:
                test_conditions = conditions

            test_parser = TestVisitor({
                'result': result,
                **host_vars
            })

            failed = list()
            for condition in test_conditions:
                if not test_parser.safe_eval(condition):
                    result.failed = True
                    failed.append(condition)

            setattr(result, 'failed_tests', failed)
            return result

        return wrapper

    return decorator
