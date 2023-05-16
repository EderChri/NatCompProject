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
            edges = [(new_vertex_id, i) for i in range(self.vcount() - 1) if random() <= 0.25]
            self.add_edges(edges)


class CityVillageGraph(Graph):
    villages = []
    city = None

    def __init__(self, number_connections=3, *args, **kwds):
        super().__init__(*args, **kwds)
        self.nr_connections = number_connections
        self.city = None
        self.villages = None

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

    def add_locations(self, city, villages):
        # If city has not been added yet, add city and
        # connections between city and village
        filename = './output.txt'
        self.city = city
        self.villages = villages
        self += city
        for village in villages:
            self += village

        # add nr_connections many edges between each village and city
        for _ in range(self.nr_connections):
            # add number of vertexes in city to fix problem with vertex numbers in overall graph
            idx = city.vcount()
            for village in villages:
                village_node = choice(village.vs)
                city_node = choice(city.vs)
                # possible solution: add city size and size previous villages to village_node.index
                self.add_edge(village_node.index + idx, city_node.index)
                # add number of vertexes in village to fix problem with vertex numbers in overall graph
                idx = idx + village.vcount()
                with open(filename, 'w') as f:
                    print(city, file=f)
                    print(village, file=f)
                    print(self, file=f)

        self.vs["state"] = "ignorant"
        return self

    def make_complete_graph(self):
        self.add_edges([(i, j) for i in range(self.vcount()) for j in range(i + 1, self.vcount())])

    def get_igraph_representation(self):
        igraph = Graph()
        igraph.add_vertices(self.vcount())
        igraph.add_edges(self.get_edgelist())
        return igraph
    
    def all_informed(self):
        if all(i == 'not_interested' for i in self.vs['state']):
            informed = True
        else:
            informed = False
        return informed

    def spread_information(self, spread_prob=0.25):

        nr_not_interested = 0
        nr_spreading = 0

        for node_idx in self.vs.indices:
            # Node has nothing to share
            if self.vs[node_idx]["state"] == "ignorant":
                continue

            if self.vs[node_idx]["state"] == "not_interested":
                nr_not_interested += 1
                continue

            neigh_idxs = self.incident(self.vs[node_idx]["name"], mode="out")

            if all(self.vs[neigh_idxs]["state"] == "spreading" or self.vs[neigh_idxs]["state"] == "not_interested"):
                self.vs[node_idx]["state"] = "not_interested"
                nr_not_interested += 1

            for neighbour in neigh_idxs:

                if self.vs[neighbour]["state"] == "ignorant":
                    if random() < spread_prob:
                        nr_spreading += 1
                        self.vs[neighbour]["state"] = "spreading"

        return [nr_not_interested, nr_spreading, self.vcount()-nr_spreading-nr_not_interested]

