import numpy as np
from igraph import Graph


class Dwelling(Graph):
    """
    Class to represent either a village or a city
    """

    def __init__(self, number_nodes, prob, *args, **kwds):
        """
        Constructor that adds a number_nodes nodes to the graph and connects them with prob probability
        :param number_nodes: Int that indicates the number of nodes in the Dwelling
        :param prob: Float that indicates the probability of two nodes being connected by an edge in the Dwelling
        :param args: Args to be passed to super
        :param kwds: kwds to be passed to super
        """
        super().__init__(*args, **kwds)
        for _ in range(number_nodes):
            self.add_vertex()
            new_vertex_id = self.vcount() - 1
            edges = [(new_vertex_id, i) for i in range(self.vcount() - 1) if np.random.random() <= prob]
            self.add_edges(edges)


class CityVillageGraph(Graph):
    """
    Class to represent graph of network of city and villages
    """
    villages = []
    city = None

    def __init__(self, number_connections=3, spreading_time=5, time_out=True, *args, **kwds):
        """
        Constructor to set additional properties
        :param number_connections: Int to indicate the mean number of connections between the city and a village
        :param spreading_time: Int indicating the time a node spreads if in spreading state and neighbours are in
            ignorant state
        :param time_out: Boolean indicating whether nodes stop spreading after some iterations or not
        :param args: args to be passed to super
        :param kwds: kwds to be passed to super
        """
        super().__init__(*args, **kwds)
        self.nr_connections = number_connections
        self.time_out = time_out
        self.city = None
        self.villages = None
        self.spreading_time = spreading_time

    def __add__(self, other):
        """
        Overwritting the default __add__ of igraph.Graph __add__ to keep class properties
        :param other:
        :return: self
        """
        tmp_vil = self.villages
        tmp_city = self.city
        tmp_nr_con = self.nr_connections
        tmp_spreading_time = self.spreading_time
        tmp_time_out = self.time_out
        self = super().__add__(other)
        self.city = tmp_city
        self.villages = tmp_vil
        self.nr_connections = tmp_nr_con
        self.spreading_time = tmp_spreading_time
        self.time_out = tmp_time_out
        return self

    def add_dwellings(self, city, villages):
        """
        Adds a city and a list of villages to the graph
        :param city: Dwelling object that represents the city
        :param villages: List of Dwelling objects that represent the villages
        :return: self
        """
        # If city has not been added yet, add city and
        # connections between city and village
        filename = './output.txt'
        self.city = city
        self.villages = villages
        self += city
        for village in villages:
            self += village

        # add number of vertexes in city to fix problem with vertex numbers in overall graph
        idx = city.vcount()
        # add nr_connections many edges between each village and city
        for village in villages:
            number_connections = int(abs(np.random.normal(self.nr_connections - 1))) + 1
            for _ in range(number_connections):
                village_node = np.random.choice(village.vs)
                city_node = np.random.choice(city.vs)
                # possible solution: add city size and size previous villages to village_node.index
                self.add_edge(village_node.index + idx, city_node.index)
                # add number of vertexes in village to fix problem with vertex numbers in overall graph
                with open(filename, 'w') as f:
                    print(city, file=f)
                    print(village, file=f)
                    print(self, file=f)
            idx = idx + village.vcount()

        # Set initial properties of nodes
        self.vs["state"] = "ignorant"
        self.vs["action"] = False
        self.vs["time"] = self.spreading_time
        return self

    def make_complete_graph(self):
        """
        Helper function to make the graph complete i.e, every node is connected with every other node in the graph
        :return:
        """
        self.add_edges([(i, j) for i in range(self.vcount()) for j in range(i + 1, self.vcount())])

    def get_igraph_representation(self):
        """
        Helper function to convert the VillageCityGraph to an igraph object. Used for plotting
        :return: igraph.Graph representation of self
        """
        igraph = Graph()
        igraph.add_vertices(self.vcount())
        igraph.add_edges(self.get_edgelist())
        return igraph

    def not_spreading(self):
        """
        Checks whether all nodes stopped spreading in the graph
        :return: Boolean
        """
        if all(i != 'spreading' for i in self.vs['state']):
            not_spreading = True
        else:
            not_spreading = False
        return not_spreading

    def spread_information(self, nr_not_interested=0, nr_spreading=0, spread_prob=0.4):
        """
        Method used to run one iteration of spreading information.
        :param nr_not_interested: Int indicating the number of not_interested nodes at the beginning of the iteration
        :param nr_spreading: Int indicating the number of spreading nodes at the beginning of the iteration
        :param spread_prob: Float indicating the spreading probability for this iteration
        :return: List of integers indicating the number of not_interested, spreading and ignorant nodes after iteration
        """
        self.vs["action"] = False

        for node_idx in self.vs.indices:

            # Node has nothing to share
            if self.vs[node_idx]["state"] == "ignorant":
                continue

            if self.vs[node_idx]["state"] == "not_interested":
                continue

            neigh_idxs = self.neighborhood(self.vs[node_idx], order=1, mindist=1)
            # only reduce when using iterations to change from spreading to not interested
            if self.time_out:
                self.vs[node_idx]["time"] -= 1
            if (all(self.vs[neigh]["state"] == "spreading" or
                    self.vs[neigh]["state"] == "not_interested" for neigh in neigh_idxs) or self.vs[node_idx][
                    "time"] <= 0) and \
                    not self.vs[node_idx]["action"]:
                self.vs[node_idx]["state"] = "not_interested"
                self.vs[node_idx]["action"] = True
                nr_not_interested += 1
                nr_spreading -= 1

            for neighbour in neigh_idxs:
                if self.vs[neighbour]["state"] == "ignorant":
                    if np.random.random() < spread_prob and not self.vs[neighbour]["action"]:
                        nr_spreading += 1
                        self.vs[neighbour]["action"] = True
                        self.vs[neighbour]["state"] = "spreading"

        return [nr_not_interested, nr_spreading, self.vcount() - nr_spreading - nr_not_interested]
