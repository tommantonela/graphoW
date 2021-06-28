import math
from collections import Counter
from collections import defaultdict
import matplotlib.pyplot as plt
from statistics import mean

import networkx as nx
import numpy as np

import spacy
from sklearn.cluster import KMeans


class TextGraph:
    """Base class to represent a graph of words inspired in "Graph-of-word and TW-IDF: new approach to ad hoc IR"

    Attributes
    ----------
    graph : DiGraph
        the structure supporting the graph of words

    language_models: dict
        'static' dictionary containing a mapping between the supported languages and the corresponding model.

     Methods
    -------
    _text2graph:
	    Builds the graph-of-words.
    process_text:
	    Pre-process the text into a list of tokens.
    statistics:
	    Computes statistics and speech graph attributes based on "Graph analysis of dream reports is especially informative about psychosis".
    narrative_consistency:
        Computes the narrative consistency of the graph according to the definitions in "Measuring Narrative Fluency by Analyzing Dynamic Interaction Networks in Textual Narratives"
    narrative_consistency_keyword:
        Computes the keyword narrative consistency of the graph according to the definitions in "Measuring Narrative Fluency by Analyzing Dynamic Interaction Networks in Textual Narratives"
    plot_graph:
	    Plots the graph of words based on a Kamada Kawai layout.
    """

    language_models = {'en': 'en_core_web_sm', 'es': 'es_core_news_sm', 'ch': 'zh_core_web_sm', 'da': 'da_core_news_sm',
                       'nl': 'nl_core_news_sm', 'fr': 'fr_core_news_sm', 'de': 'de_core_news_sm',
                       'gr': 'el_core_news_sm',
                       'it': 'it_core_news_sm', 'ja': 'ja_core_news_sm', 'lt': 'lt_core_news_sm',
                       'multi': 'xx_ent_wiki_sm',
                       'no': 'nb_core_news_sm', 'po': 'pl_core_news_sm', 'pt': 'pt_core_news_sm',
                       'ro': 'ro_core_news_sm',
                       'ru': 'ru_core_news_sm'
                       }
    nlp = None

    def __init__(self, text, **kwargs):
        """
        Parameters
        ----------
        text : str
            the text to build the graph

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

        model = kwargs.get('model')
        if model is None:
            model = TextGraph.language_models.get(kwargs.get('lang', 'multi'), None)

        if model is None:
            raise RuntimeError('Unknown language. Supported languages:', TextGraph.language_models.keys())

        if not spacy.util.is_package(model):
            spacy.cli.download(model)

        TextGraph.nlp = spacy.load(model)

        self.graph = self._text2graph(text, kwargs.get('lemma', False), kwargs.get('window', 2))

    def _text2graph(self, text, lemma=False, window=2):
        """
        Builds the graph-of-words

          Parameters
          ----------
          text : str
            the text to build the graph

          window : int, optional
            The size of the co-occurrence window to consider. By default ``window = 2``. Meaning that a word at position
             ``n`` will be related to the word at position ``n+1``.
             For example in the text "harry potter wins", the following relations will be included in the graph:
             ``(harry, potter)``, ``(potter, "wins").

          lemma : boolean, optional
            Whether to consider the lemma of the words in graph creation or not. Be default ``lemma = False``, meaning
            that no lemamatization will be applied.

          """

        words = self.process_text(text, lemma)
        gr = nx.DiGraph()
        edge_count = Counter(
            [(words[start], words[start + end], 1) for start in range(len(words)) for end in range(1, window) if
             start + end < len(words)])
        gr.add_weighted_edges_from((k[0], k[1], v) for k, v in edge_count.items())
        return gr

    def process_text(self, text, lemma=False):
        """
            Pre-process the text into a list of tokens.
            Nodes represent the words in the original graph without any pre - processing.
            Only punctuation marks are removed.

          Parameters
          ----------
          text : str
            the text to build the graph

          lemma : boolean, optional
            Whether to consider the lemma of the words in graph creation or not.
            By default ``lemma = False``, meaning that no lemamatization will be applied.

          Returns
          -------
          list
              the list of tokens obtained from the text
          """
        processed_text = TextGraph.nlp(text.lower())
        words = [t.text.strip() if not lemma else t.lemma_ for t in processed_text if not t.is_punct]
        return words

    def statistics(self):
        """Computes statistics and speech graph attributes based on "Graph analysis of dream reports is especially informative about psychosis":
            General attributes:
                * number_of_nodes.
                * number_of_edges.
            Connected component attributes:
                * NCC. Number of weakly connected components.
                * NSC. Number of strongly connected components.
                * LCC. Number of nodes in the largest weakly connected components.
                * LSC. Number of nodes in the largest strongly connected components.
            Recurrence attributes:
                * PE. Parallel Edges: sum of all parallel edges linking the same pair of nodes.
            Cycles:
                * L1. Cycles of one one computed as the trace of the adjacency matrix.
                * L2. Cycles of two nodes computed as the trace of the squared adjacency matrix divided by 2.
                * L3. Cycles of two nodes computed as the trace of the cubed adjacency matrix divided by 3.
            Global attributes:
                * degree_average.
                * degree_std.
                * density.
                * diameter. Length of the longest shortest path in the graph
                * average_shortest_path. Average length of the shortest path between all pairs of nodes in the graph.
                * clustering_coefficient. Average clustering coefficient. The coefficient is defined as the fraction of
                    all possible directed triangles in the graph.

         Returns
         -------
          dict
              a dictionary containing the described metrics
          """
        res = {}
        res['number_of_nodes'] = self.graph.number_of_nodes()
        res['number_of_edges'] = self.graph.number_of_edges()

        res['PE'] = sum(1 for x in self.graph.edges(data=True) if x[2]['weight'] > 1)
        res['NCC'] = nx.algorithms.components.number_weakly_connected_components(self.graph)
        res['NSC'] = nx.algorithms.components.number_strongly_connected_components(self.graph)

        res['LCC'] = max(nx.weakly_connected_components(self.graph), key=len)
        res['LSC'] = max(nx.strongly_connected_components(self.graph), key=len)

        degrees = [x[1] for x in self.graph.degree()]
        res['degree_average'] = np.mean(degrees)
        res['degree_std'] = np.std(degrees)

        adj_matrix = nx.linalg.adj_matrix(self.graph).toarray()
        adj_matrix2 = np.dot(adj_matrix, adj_matrix)
        adj_matrix3 = np.dot(adj_matrix2, adj_matrix)

        res['L1'] = np.trace(adj_matrix)
        res['L2'] = np.trace(adj_matrix2) / 2
        res['L3'] = np.trace(adj_matrix3) / 3

        res['density'] = 2 * res['number_of_edges'] / (res['number_of_nodes'] * (res['number_of_nodes'] - 1))

        shortest_paths = [i for x in nx.shortest_path_length(self.graph) for i in x[1].values() if i > 0]
        res['diameter'] = max(shortest_paths)
        res['average_shortest_path'] = mean(shortest_paths)
        res['clustering_coefficient'] = mean(nx.clustering(self.graph).values())

        return res

    def narrative_consistency(self, metric='betweenness', nodes=None):  # measures centrality
        """Computes the narrative consistency of the graph according to the definitions in "Measuring Narrative Fluency by Analyzing Dynamic Interaction Networks in Textual Narratives"
           The consistency is computed as the entropy of the centrality of entities/words.

          Parameters
          ----------
          metric : str, optional
              The metric on which base the consistency.
              Options: betweenness, degree, closeness centrality, mean (arithmetic mean of the three metrics)
              Default is betweenness.
          nodes : nodes, optional
              Entities over which compute the consistency. If None, all words are considered.
              Default is None.

          Returns
          -------
          float
              The narrative consistency of the graph.
          """
        if metric == 'betweenness':
            vals = nx.betweenness_centrality(self.graph)
        elif metric == 'degree':
            vals = {n[0]: n[1] for n in self.graph.degree()}
        elif metric == 'closeness':
            vals = nx.closeness_centrality(self.graph)
        else:
            vals_b = nx.betweenness_centrality(self.graph)
            vals_d = {n[0]: n[1] for n in self.graph.degree()}
            vals_c = nx.closeness_centrality(self.graph)

            min_ = min(vals_b.values())
            delta = max(vals_b.values()) - min_
            vals_b = {k: (v - min_) / delta for k, v in vals_b.items()}

            min_ = min(vals_d.values())
            delta = max(vals_d.values()) - min_
            vals_d = {k: (v - min_) / delta for k, v in vals_d.items()}

            min_ = min(vals_c.values())
            delta = max(vals_c.values()) - min_
            vals_c = {k: (v - min_) / delta for k, v in vals_c.items()}

            vals = {k: (v + vals_b.get(k, 0) + vals_c.get(k, 0)) / 3 for k, v in vals_d.items()}

        if nodes is None:
            return sum(-math.log(v) for v in vals.values() if v > 0) / self.graph.number_of_nodes()

        return sum(-math.log(v) for k, v in vals.items() if v > 0 and k in nodes) / len(nodes)

    def narrative_consistency_keyword(self, metric='betweenness'):  # measures centrality of keywords
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
               The keyword narrative consistency of the graph.
          """

        if self.graph.number_of_nodes() <= 1:
            return -1

        arr = nx.linalg.graphmatrix.adjacency_matrix(self.graph)
        kmeans = KMeans(n_clusters=2, init='k-means++', random_state=0).fit(arr)

        dd = defaultdict(int)
        cc = list(nx.closeness_centrality(self.graph).values())
        for i in range(0, len(cc)):
            dd[kmeans.labels_[i]] += cc[i]

        max_key = max(dd, key=lambda key: dd[key])
        nodes = [x[0] for x in zip(self.graph.nodes(), kmeans.labels_) if x[1] == max_key]

        return self.narrative_consistency(metric, nodes)

    def plot_graph(self):

        """Plots the graph of words based on a Kamada Kawai layout.

          Returns
          -------
          plot
              the created plot
        """
        plt.axis("off")
        pos = nx.kamada_kawai_layout(self.graph)
        return nx.draw_networkx(self.graph, pos=pos, node_size=400)


class PosTextGraph(TextGraph):
    """Class implementing a graph in which nodes represent the part-of-speech tags of each of the words in the text.
        Punctuation marks are removed and no lemmatization is performed before pos-tagging.

    Methods
    -------
    process_text:
	    Pre-process the text into a list of tokens.
    """

    def process_text(self, text, lemma=False):
        """See :func:`~TextGraph.process_text`
        """
        processed_text = TextGraph.nlp(text.lower())
        words = [t.pos_ for t in processed_text if not t.is_punct]
        return words


class NounTextGraph(TextGraph):
    """Class implementing a graph in which nodes represent the nouns.
        Only punctuation marks are removed.

    Methods
    -------
    process_text:
	    Pre-process the text into a list of tokens.
    """

    def process_text(self, text, lemma):
        """See :func:`~TextGraph.process_text`
        """
        processed_text = TextGraph.nlp(text.lower())
        words = [t.lemma_ if lemma else t.text.strip() for t in processed_text if t.pos_.startswith("NOUN")]
        return words


class NounChunksTextGraph(TextGraph):
    """Class implementing a graph in which nodes represent the found noun_chucks.
        Lemmatization has no effect over this graph

    Methods
    -------
    process_text:
	    Pre-process the text into a list of tokens.
    """

    def process_text(self, text, lemma=False):
        """See :func:`~TextGraph.process_text`
        """
        processed_text = TextGraph.nlp(text.lower())
        words = [t.text.strip() for t in processed_text.noun_chunks]
        return words
