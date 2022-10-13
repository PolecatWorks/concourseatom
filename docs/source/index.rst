.. concourse-merge documentation master file, created by
   sphinx-quickstart on Sat Sep 17 15:19:09 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to concourse-merge's documentation!
===========================================

**Concourse Merge** is a python library to allow merging of concourse plans. It flattens the :class:'Resource' and :class"'ResourceType' during the merge to ensure the final results do not include duplicates.
it also provides intelligent renaming of references to the renaming to ensure the function of the originating plans stays consistent through the merge.

Check out the :doc:`usage` section for further information.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   modules
   development
   api
   todo

Copyright
=======
Copyright (C) 2022 Ben Greene



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
