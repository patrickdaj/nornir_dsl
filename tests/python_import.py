from nornir_utils.plugins.tasks.data import echo_data


def imported_task(task):
    task.run(echo_data, name="in imported", x=1)


__all__ = ["imported_task"]
