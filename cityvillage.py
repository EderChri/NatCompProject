from random import random, choice

import numpy as np
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
            edges = [(new_vertex_id, i) for i in range(self.vcount() - 1) if random() <= 0.25]
            self.add_edges(edges)


class CityVillageGraph(Graph):
    villages = []
    city = None

    def __init__(self, number_connections=3, spreading_time=5, time_out=True, *args, **kwds):
        super().__init__(*args, **kwds)
        self.nr_connections = number_connections
        self.time_out = time_out
        self.city = None
        self.villages = None
        self.spreading_time = spreading_time

    def __add__(self, other):
        # Needed so the igraph.Graph addition works
        # But the class properties are kept as well
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

    def add_locations(self, city, villages):
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
                village_node = choice(village.vs)
                city_node = choice(city.vs)
                # possible solution: add city size and size previous villages to village_node.index
                self.add_edge(village_node.index + idx, city_node.index)
                # add number of vertexes in village to fix problem with vertex numbers in overall graph
                with open(filename, 'w') as f:
                    print(city, file=f)
                    print(village, file=f)
                    print(self, file=f)
            idx = idx + village.vcount()

        self.vs["state"] = "ignorant"
        self.vs["action"] = False
        self.vs["time"] = self.spreading_time
        return self

    def make_complete_graph(self):
        self.add_edges([(i, j) for i in range(self.vcount()) for j in range(i + 1, self.vcount())])

    def get_igraph_representation(self):
        igraph = Graph()
        igraph.add_vertices(self.vcount())
        igraph.add_edges(self.get_edgelist())
        return igraph

    def not_spreading(self):
        if all(i != 'spreading' for i in self.vs['state']):
            not_spreading = True
        else:
            not_spreading = False
        return not_spreading

    def spread_information(self, spread_prob=0.4):

        nr_not_interested = 0
        nr_spreading = 0
        self.vs["action"] = False

        for node_idx in self.vs.indices:

            # Node has nothing to share
            if self.vs[node_idx]["state"] == "ignorant":
                continue

            if self.vs[node_idx]["state"] == "not_interested":
                nr_not_interested += 1
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

            for neighbour in neigh_idxs:
                if self.vs[neighbour]["state"] == "ignorant":
                    if random() < spread_prob and not self.vs[neighbour]["action"]:
                        nr_spreading += 1
                        self.vs[neighbour]["action"] = True
                        self.vs[neighbour]["state"] = "spreading"

        return [nr_not_interested, nr_spreading, self.vcount() - nr_spreading - nr_not_interested]
