from random import random, choice
from igraph import Graph


class Village(Graph):
    def __init__(self, number_nodes, name, *args, **kwds):
        super().__init__(*args, **kwds)
        self.name = name
        for _ in range(number_nodes):
            self.add_vertex()
            new_vertex_id = self.vcount() - 1
            edges = [(new_vertex_id, i) for i in range(self.vcount() - 1)]
            self.add_edges(edges)


class City(Graph):
    def __init__(self, number_nodes, *args, **kwds):
        super().__init__(*args, **kwds)
        for _ in range(number_nodes):
            self.add_vertex()
            new_vertex_id = self.vcount() - 1
            edges = [(new_vertex_id, i) for i in range(self.vcount() - 1) if random() <= 0.3]
            self.add_edges(edges)


class CityVillageGraph(Graph):

    villages = []
    city = None

    def __init__(self, number_connections=3, *args, **kwds):
        super().__init__(*args, **kwds)
        self.nr_connections = number_connections

    def __add__(self, other):
        # Needed so the igraph.Graph addition works
        # But the class properties are kept as well
        tmp_vil = self.villages
        tmp_city = self.city
        tmp_nr_con = self.nr_connections
        self = super().__add__(other)
        self.city = tmp_city
        self.villages = tmp_vil
        self.nr_connections = tmp_nr_con
        return self

    def add_location(self, location):
        # If city has not been added yet, add city and
        # connections between city and village
        if isinstance(location, City):
            self += location
            self.city = location
            # add nr_connections many edges between each village and city
            for _ in range(self.nr_connections):
                for village in self.villages:
                    village_node = choice(village.vs)
                    city_node = choice(self.city.vs)
                    self.add_edge(village_node.index, city_node.index)

        # Add the location to the graph
        if isinstance(location, Village):
            self.villages.append(location)
            self += location

            # If city is already set, add nr_connections many edges
            # between the village and the city
            if self.city is not None:
                for _ in range(self.nr_connections):
                    village_node = choice(location.vs)
                    city_node = choice(self.city.vs)
                    self.add_edge(village_node.index, city_node.index)
        return self

    def make_complete_graph(self):
        self.add_edges([(i, j) for i in range(self.vcount()) for j in range(i+1, self.vcount())])

    def get_igraph_representation(self):
        igraph = Graph()
        igraph.add_vertices(self.vcount())
        igraph.add_edges(self.get_edgelist())
        return igraph

