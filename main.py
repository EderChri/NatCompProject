from cityvillage import City, Village, CityVillageGraph
import igraph
import random

random.seed(42)
def run_simulation():
    villages = [Village(number_nodes=10, name=f"village_{i}") for i in range(3)]
    city = City(number_nodes=40)
    graph = CityVillageGraph()
    graph = graph.add_locations(city,villages)
    out = igraph.plot(graph.get_igraph_representation(), target='test.png',
                      bbox=(800, 800),
                      margin=50,
                      vertex_label=None, edge_width=1, edge_color='black')
    out.save("test.png")

if __name__ == '__main__':
    run_simulation()