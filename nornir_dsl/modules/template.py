from functools import wraps
from typing import Callable, Union, List, Dict, Any
from nornir.core.task import Result
from nornir.core.helpers.jinja_helper import render_from_string

def template(
    pb_vars: Dict[str, Any],
) -> Callable[..., Any]:
    def decorator(wrapped) -> Callable[..., Any]:
        @wraps(wrapped)
        def wrapper(task: Callable[..., Any], **kwargs: Dict[str, Any]) -> Result:

            if pb_vars.get(task.host.name, None):
                host_vars = pb_vars.get(task.host.name)
            else:
                host_vars = {}
            
            host_vars['task'] = task

            for key, value in kwargs.items():
                if isinstance(value, str):
                    kwargs[key] = render_from_string(value, **host_vars)

            return wrapped(task, **kwargs)

        return wrapper

    return decorator