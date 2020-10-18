nornir_dsl
##########
Just for fun making an Ansible-ish DSL with Nornir backend.  Currently more or less works with until, when, test, 
and assert.  Filtering on inventory seems to work and imports work.  Want to add import of tasks, debugging keywords,
templating, loops...a bunch of stuff.

It uses decorators pretty heavily and quite a few evals but they are done safely using the python ast module.

DSL Format
----------

.. code-block:: yaml

    ---
    - name: playbook1
      output: [results, failed_tests]
    
      import:
        - nornir_utils.plugins.tasks.data
        - nornir_netmiko.tasks

      tasks_import:
        - blah.yaml

      tasks:
        - name: Run task with when and until
          task: netmiko_send_command
          kwargs:
            command_string: show high-availability state
            use_textfsm: true
          when:
            - task.host.platform == 'panos'
          until:
            - result.result['state'] == 'active'

        - name: Run task with test and assert
          task: netmiko_send_command
          kwargs:
            command_string: show system info
            use_textfsm: true
          test:
            - result.result['sw-version'] == '8.1.15'
          assert:
            - result.result.get('sw-version', None)

Installation

.. code-block:: shell

    git clone https://github.com/patrickdaj/nornir_dsl.git
    cd nornir_dsl
    poetry install

Running
-------

.. code-block:: shell

    $ nornir-cli --help
    nornir-cli
    Usage: nornir-cli [OPTIONS] COMMAND [ARGS]...

    Options:
      --config PATH  Path to Nornir config file
      --help         Show this message and exit.

    Commands:
      inv  inv FILTER FILTER should be a Nornir Advanced filter Example:...
      run  Run PLAYBOOK

    $ nornir-cli inv --help
    Usage: nornir-cli inv [OPTIONS] FILTER_STR

      inv FILTER

    FILTER should be a Nornir Advanced filter

    Example: "F(platform__any=['linux', 'windows'] & F(testbed='tb100')"

    Options:
      --vars  Output all vars
      --help  Show this message and exit.

    $ nornir-cli run --help
    Usage: nornir-cli run [OPTIONS] PLAYBOOK

      Run PLAYBOOK

    Options:
      --step  Step through playbook
      --help  Show this message and exit.