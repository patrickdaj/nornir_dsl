nornir_dsl
##########

DSL Format
----------

.. code-block:: yaml

    ---
    hosts:
    defaults:
      print: true

    modules:
      - { nornir_napalm.tasks, ['napalm_get', 'napalm_cli']}

    tasks:
      - name:
        module: napalm_get
        args:
        when:
        until:
        assert:
        debug:
        print: true
    
      