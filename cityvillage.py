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
        self.city = None
        self.villages = None

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
            #add number of vertexes in city to fix problem with vertex numbers in overall graph
            idx = city.vcount()
            for village in villages:
                village_node = choice(village.vs)
                city_node = choice(city.vs)
                #possible solution: add city size and size previous villages to village_node.index
                self.add_edge(village_node.index+idx, city_node.index)
                #add number of vertexes in village to fix problem with vertex numbers in overall graph
                idx = idx + village.vcount()
                with open(filename, 'w') as f:
                    print(city, file=f)
                    print(village, file=f)
                    print(self,file=f)

        return self

    def make_complete_graph(self):
        self.add_edges([(i, j) for i in range(self.vcount()) for j in range(i+1, self.vcount())])

    def get_igraph_representation(self):
        igraph = Graph()
        igraph.add_vertices(self.vcount())
        igraph.add_edges(self.get_edgelist())
        return igraph
