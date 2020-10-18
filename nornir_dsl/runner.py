import importlib
from ruamel.yaml import load, SafeLoader
from nornir.core.helpers.jinja_helper import render_from_string

from nornir_dsl import modules
from nornir_dsl.utils.safe_evals import InventoryVisitor

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

        output = pb.pop("output", None)

        if pb.get("filter", None):
            inv_parser = InventoryVisitor()
            filtered = nornir.filter(inv_parser.safe_eval(pb.get("filter")))
        else:
            filtered = nornir

        pb_vars = dict()
        pb_imports = dict()

        for module in pb["import"]:
            tasks = importlib.import_module(module)
            pb_imports.update({t: getattr(tasks, t) for t in tasks.__all__})

        for step in pb["tasks"]:

            if step.pop("debug", None):
                print(f"debug where? {step.keys()}")
                input()

            main_task = step.pop("task", None)
            
            if not main_task:
                print("Step has no task...skipping")
                print(step)

            task = pb_imports[main_task]

            register = step.pop("register", None)
            set_fact = step.pop("set_fact", None)

            if step.get("when", None):
                task = (modules.when(pb_vars, step.pop("when")))(task)

            if step.get("test", None):
                task = (modules.test(pb_vars, step.pop("test"), False))(task)

            if step.get("assert", None):
                task = (modules.test(pb_vars, step.pop("assert"), True))(task)

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

            results = filtered.run(task, **step['kwargs'])

            for result in results.values():
                if not pb_vars.get(result.host.name, None):
                    pb_vars[result.host.name] = {}
                if register:
                    pb_vars[result.host.name][register] = result
                else:
                    pb_vars[result.host.name]["last"] = result

                if set_fact:
                    for fact_key in set_fact.keys():
                        pb_vars[result.host.name].data[fact_key] = render_from_string(
                            set_fact[fact_key], result
                        )

            callback(results, vars=output)