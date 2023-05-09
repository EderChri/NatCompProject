from igraph import Graph


class Location:
    """
    A class to represent a node in the graph, which can be either a city or a village.

    Attributes:
    - id (int): a unique identifier for the location.
    - populations (set): a set of Population objects representing the population living in the location.
    - connections (list): a list of Location objects representing the connections to other locations.
    """

    def __init__(self, id):
        self.id = id
        self.populations = set()
        self.connections = []


class Population:
    """
    A class to represent a group of people living in a location.

    Attributes:
    - id (int): a unique identifier for the population.
    """

    def __init__(self, id):
        self.id = id


class City(Location):
    """
    A subclass of Location to represent the city.

    Attributes:
    - id (int): a unique identifier for the city.
    - populations (set): a set of Population objects representing the population living in the city.
    - connections (list): a list of Location objects representing the connections to other locations.
    """

    def __init__(self, id):
        super().__init__(id)

    def add_population(self, population):
        """
        Adds a Population object to the set of populations living in the city.

        Parameters:
        - population (Population): a Population object to add to the set of populations.
        """
        self.populations.add(population)


class Village(Location):
    """
    A subclass of Location to represent the village.

    Attributes:
    - id (int): a unique identifier for the village.
    - populations (set): a set of Population objects representing the population living in the village.
    - connections (list): a list of Location objects representing the connections to other locations.
    """

    def __init__(self, id):
        super().__init__(id)

    def add_fully_connected_population(self, population):
        """
        Adds a set of Population objects to the village, and connects all nodes in the set.

        Parameters:
        - population (set): a set of Population objects to add to the village and connect fully.
        """
        self.populations.update(population)
        for node1 in population:
            for node2 in population:
                if node1 != node2:
                    node1.add_edges([node2])


class CityVillageGraph:
    """
    A class to represent the overall graph of the city and its surrounding villages.

    Attributes:
    - locations (list): a list of Location objects representing the nodes in the graph.
    """

    def __init__(self):
        self.locations = []

    def add_location(self, location):
        """
        Adds a Location object to the graph.

        Parameters:
        - location (Location): a Location object to add to the graph.
        """
        self.locations.append(location)

    def to_igraph(self):
        """
        Converts the CityVillageGraph object to an igraph.Graph object.

        Returns:
        - ig (igraph.Graph): an igraph.Graph object representing the graph.
        """
        node_dict = {}  # to keep track of which Population object corresponds to which node in the igraph.Graph object
        edges = []  # to keep track of the edges in the graph

        for location in self.locations:
            for population in location.populations:
                node_dict[population] = len(node_dict)  # assign a unique index to each Population object

        ig = Graph(len(node_dict))  # create a new igraph.Graph object with the appropriate number of nodes

        for location in self.locations:
            for population in location.populations:
                node_index = node_dict[population]  # get the index of the corresponding node
                ig.vs[node_index]["label"] = str(population.id)  # set the label of the node to the population id

            for connection in location.connections:
                for population1 in location.populations:
                    for population2 in connection.populations:
                        edge = (node_dict[population1], node_dict[population2])
                        if edge not in edges:
                            edges.append(edge)

        ig.add_edges(edges)  # add the edges to the igraph.Graph object

        return ig
