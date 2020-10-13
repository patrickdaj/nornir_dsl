import importlib
from ruamel.yaml import load, SafeLoader
from ipdb import launch_ipdb_on_exception, runcall

from nornir_dsl import modules


default_callback = ["nornir_utils.plugins.functions.print_result", "print_result"]


def get_runner(nornir, playbook, step):
    pb_json = load(playbook.read(), Loader=SafeLoader)

    for pb in pb_json:

        callback = getattr(
            importlib.import_module(
                pb.get("callback") if pb.get("callback", None) else default_callback[0]
            ),
            "callback" if pb.get("callback", None) else default_callback[1],
        )

        pb_vars = dict()
        pb_imports = dict()

        for module in pb["import"]:
            tasks = importlib.import_module(module)
            pb_imports.update({t: getattr(tasks, t) for t in tasks.__all__})

        for step in pb["tasks"]:

            task = pb_imports[step.pop("task")]

            register = step.pop("register", None)

            if step.get("when", None):
                task = (modules.when(pb_vars, step.pop("when")))(task)

            if step.get("test", None):
                fail_task = step.pop('fail_task', None)
                task = (modules.test(pb_vars, step.pop("test"), fail_task))(task)

            if step.get("until", None):
                retries = step.pop("retries", None)
                delay = step.pop("delay", None)
                initial_delay = step.pop("initial_delay", None)
                reset_conn = step.pop("reset_conn", None)
                task = (
                    modules.until(
                        pb_vars,
                        step.pop("until"),
                        initial_delay,
                        retries,
                        delay,
                        reset_conn,
                    )
                )(task)

            task = (modules.template(pb_vars))(task)

            results = nornir.run(task, **step)

            for result in results.values():
                if not pb_vars.get(result.host.name, None):
                    pb_vars[result.host.name] = {}
                if register:
                    pb_vars[result.host.name][register] = result
                else:
                    pb_vars[result.host.name]["last"] = result

            callback(results)
