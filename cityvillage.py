from random import random
from igraph import Graph


class Village(Graph):
    def __init__(self, number_nodes, id):
        super().__init__()
        self.id = id
        for _ in number_nodes:
            self.add_vertex()
            new_vertex_id = self.vcount() - 1
            edges = [(new_vertex_id, i) for i in range(self.vcount() - 1)]
            self.add_edges(edges)


class City(Graph):
    def __init__(self, number_nodes):
        super().__init__()
        for _ in number_nodes:
            self.add_vertex()
            new_vertex_id = self.vcount() - 1
            edges = [(new_vertex_id, i) for i in range(self.vcount() - 1) if random() <= 0.3]
            self.add_edges(edges)


class CityVillageGraph(Graph):

    villages = set()
    city = None

    def add_location(self, location):
        if isinstance(location, City):
            self.city = location
            self.union(location)
