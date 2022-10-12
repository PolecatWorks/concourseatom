Development
===========


To install concourseatom and include the tools/libraries to do development.

.. code-block:: console

    (.venv) $ pip install concourseatom[dev]

Once this installed you can then run tests with and build docs as follows.

.. code-block:: console

    pytest
    make docs



Sample Usage in code
--------------------

Setup a simple Resource

>>> from concourseatom import models
>>> models.get_random_ingredients()
['shells', 'gorgonzola', 'parsley']


Usage examples:

>>> 1 + 1
2

.. todo:: apie
    Add some more todos here
