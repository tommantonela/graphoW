graphoW: A python package for building Graph of Words 
=====================================================

graphoW is a Python package for the creation of a Graph-of-Words (GoW) representation of texts.

- Structure is based on: `Graph-of-word and TW-IDF: new approach to ad hoc IR <https://dl.acm.org/doi/abs/10.1145/2505515.2505671>`_
- Graph metrics are based on: `Graph analysis of dream reports is especially informative about psychosis <https://www.nature.com/articles/srep03691?hc_location=ufi>`_
- Narrative consistency and rapidity are based on: `Measuring Narrative Fluency by Analyzing Dynamic Interaction Networks in Textual Narratives <http://ceur-ws.org/Vol-2593/paper2.pdf>`_

It allows to:

- Create a GoW for individual texts.

- Create a container of GoW in which each GoW corresponds to a paragraph in the text. 

- Compute diverse types of graph metrics (e.g., individual, global, connectivity...).

- Compute the narrative consistency of text based on all terms or only on noun phrases.

- Compute the rapidity of a text, i.e., how slow/fast change the structure of paragraphs.

GoW is supported using ``NetworkX``. The graph structures can be retrieved, which allows using all metrics and techniques already implemented in ``NetworkX``. 


License
-------
.. include:: ../../LICENSE.txt

.. toctree::
   :maxdepth: 1
   :hidden:

   install
   tutorial
   reference/index
   developer/index

