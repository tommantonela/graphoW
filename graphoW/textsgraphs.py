from collections import defaultdict

import re
from statistics import mean
import networkx as nx

import karateclub
import sklearn

from graphoW.textgraph import NounChunksTextGraph, TextGraph, PosTextGraph, NounTextGraph


class TextsGraphs:

    """Class for processing multiple textual units. One graph is kept for each unit.
        The default textual unit is the paragraph

    Attributes
    ----------
    parapraphs : list(DiGraph)
        The structure supporting the graphs for each paragraph

    Methods
    -------
        narrative_consistency:
           Computes the narrative consistency of the text according to the definitions in "Measuring Narrative Fluency by Analyzing Dynamic Interaction Networks in Textual Narratives"
        narrative_consistency_keyword:
          Computes the keyword narrative consistency of the text according to the definitions in "Measuring Narrative Fluency by Analyzing Dynamic Interaction Networks in Textual Narratives"
        rapidity:
          Computes the rapidity of narrative development of the graph according to the definitions in "Measuring Narrative Fluency by Analyzing Dynamic Interaction Networks in Textual Narratives"

    """

    def __init__(self, filename, graph_type='naive', **kwargs):

        """
        Parameters
        ----------

        filename : str
            Path to the file with the text to process

        graph_type : str, optional
            Description of arg1

        lang : str, optional
            Language on which the text to represent is written. By default, ``multi`` is selected.
            Supported languages include: Spanish, English, Italian, Portuguese, Russian, Chinese, ...

        window : int, optional
            The size of the co-occurrence window to consider. By default ``window = 2``. Meaning that a word at position
             ``n`` will be related to the word at position ``n+1``.
             For example in the text "harry potter wins", the following relations will be included in the graph:
             ``(harry, potter)``, ``(potter, "wins").

        lemma : boolean, optional
            Whether to consider the lemma of the words in graph creation or not. Be default ``lemma = False``, meaning
            that no lemamatization will be applied.

        Raises
        ------
        RuntimeError
           If the selected language is not supported by ``TextGraph``.
        """

        texts = open(filename, encoding="utf8").read()
        paragraphs = re.split(r"\r\n|\r|\n", texts)

        self.paragraphs = []
        for p in paragraphs:

            if len(p) <= 1:
                continue

            if graph_type == 'naive':
                gg = TextGraph(p, **kwargs)
            elif graph_type == 'pos':
                gg = PosTextGraph(p, **kwargs)
            elif graph_type == 'noun':
                gg = NounTextGraph(p, **kwargs)
            elif graph_type == 'nounChunks':
                gg = NounChunksTextGraph(p, **kwargs)
            else:
                raise RuntimeError('Unknown graph type')
            if gg.graph.number_of_edges() > 0:
                self.paragraphs.append(gg)
                                       
    def __iter__(self):
        return iter(self.paragraphs)

    def narrative_consistency(self,metric='betweenness'):  # measures centrality
        """Computes the narrative consistency of the text according to the definitions in "Measuring Narrative Fluency by Analyzing Dynamic Interaction Networks in Textual Narratives"
            The consistency is computed as the average :func:`~TextGraph.narrative_consistency` of each graph.

                  Parameters
                  ----------
                  metric : str, optional
                      The metric on which base the consistency.
                      Options: betweenness, degree, closeness centrality, mean (arithmetic mean of the three metrics)
                      Default is betweenness.

                  Returns
                  -------
                  float
                      The narrative consistency of the full text.
        """

        return mean([g.narrative_consistency(metric) for g in self.paragraphs])

    def narrative_consistency_keyword(self):
        """
                 Computes the keyword narrative consistency of the graph according to the definitions in "Measuring Narrative Fluency by Analyzing Dynamic Interaction Networks in Textual Narratives"
                 Computes the ``narrative_consistency`` over a selected set of keywords. Keywords are those belonging to the cluster with the highest centrality.

                 Parameters
                 ----------
                 metric : str, optional
                     The metric on which base the consistency.
                     Options: betweenness, degree, closeness centrality, mean (arithmetic mean of the three metrics)
                     Default is betweenness.

                 Returns
                 -------
                 float
                      The keyword narrative consistency of the full text.
        """
        mean_ = [g.narrative_consistency_keyword('metric') for g in self.paragraphs]
        mean_ = 1 + (mean(mean_) if len(mean_) > 0 else 0)

        return 1 / mean_

    def rapidity(self):  # se calcula por párrafo, pero necesita todos los anteriores
        """
            Computes the rapidity of narrative development of the graph according to the definitions in "Measuring Narrative Fluency by Analyzing Dynamic Interaction Networks in Textual Narratives"
            Rapidity is measured based on the structural changes in entity networks.
            It is assumed that changes that are too slow or too fast hinder the readability of the narrative.

            To compare the structure of entity networks, they are represented using Graph2Vec.
            Then, rapidity is measured by estimating how a paragraph affects the entity network
            by comparing the entity networks before and after a paragraph.

            Returns
            -------
            float
                The rapidity of the full text.
        """

        def compute_rapidity_paragraph(graphsL1, paragraphsL):
            """

                Returns
                -------
                float
                    Euclidean distance between score for last paragraph vs all paragraphs but the last.
            """
            dict_nodes = dict()  # we need nodes to be integers starting with zero

            def join_graphs(joined, graphs):
                """
                    Joins two graphs.

                    Returns
                    -------
                    DiGraph
                        Joint graphs.
                """
                nodes = dict()
                edges = defaultdict(lambda: defaultdict(int))
                for g in graphs:
                    for n in g.nodes(data=True):
                        if n[0] not in dict_nodes:
                            dict_nodes[n[0]] = len(dict_nodes)
                        nodes[dict_nodes[n[0]]] = n[1]

                    for n in g.edges(data=True):
                        dd = edges[(dict_nodes[n[0]], dict_nodes[n[1]])]
                        for k, v in n[2].items():
                            dd[k] += v
                joined.add_nodes_from([(k, v) for k, v in nodes.items()])
                joined.add_edges_from([(k[0], k[1], v) for k, v in edges.items()])
                return joined

            networkx_graphsL1 = nx.Graph()
            networkx_graphsL1 = join_graphs(networkx_graphsL1, [x.graph for x in graphsL1])

            graph2vec = karateclub.Graph2Vec(dimensions=64, workers=4, min_count=1)

            graph2vec.fit([networkx_graphsL1])
            emb_graphsL1 = graph2vec.get_embedding()

            networkx_graphsL = join_graphs(networkx_graphsL1, [paragraphsL.graph])

            graph2vec.fit([networkx_graphsL])
            emb_graphsL = graph2vec.get_embedding()

            return sklearn.metrics.pairwise.euclidean_distances(emb_graphsL, emb_graphsL1)[0][0]

        optimal = 0.45  # the paper does not explain how to define this value

        raps = [compute_rapidity_paragraph(self.paragraphs[:i], self.paragraphs[i]) for i in range(1, len(self.paragraphs))]
        min_ = min(raps)
        delta = max(raps) - min_

        total = sum(abs(((r-min_)/delta) - optimal) for r in raps)

        return total / len(self.paragraphs)
