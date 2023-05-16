import os.path

from cityvillage import City, Village, CityVillageGraph
import igraph
import random
import matplotlib.pyplot as plt
import imageio
from os import listdir
from os.path import isfile, join


def run_simulation():
    city_size = 5
    village_size = 3
    nr_villages = 1
    villages = [Village(number_nodes=village_size, name=f"village_{i}") for i in range(nr_villages)]
    city = City(number_nodes=city_size)
    graph = CityVillageGraph()
    graph = graph.add_locations(city, villages)
    colormap = {"spreading": "red", "not_interested": "blue", "ignorant": "yellow"}

    # startpoint in village
    startpoint = city_size + random.randint(0, village_size * nr_villages) - 1
    graph.vs[startpoint]['state'] = 'spreading'
    count = 0  # used to debug while loop
    while not graph.all_informed():
        node_colors = [colormap[state] for state in graph.vs['state']]
        out = igraph.plot(graph.get_igraph_representation(),
                          bbox=(800, 800),
                          margin=50,
                          vertex_label=None, edge_width=1, edge_color='black',
                          vertex_color=node_colors)
        out.save(f"img/graph_{count}.png")
        count = count + 1
        not_interested, spreading, ignorant = graph.spread_information()
    node_colors = [colormap[state] for state in graph.vs['state']]
    out = igraph.plot(graph.get_igraph_representation(),
                      bbox=(800, 800),
                      margin=50,
                      vertex_label=None, edge_width=1, edge_color='black',
                      vertex_color=node_colors)
    out.save(f"img/graph_{count}.png")


def generate_gif():
    filenames = [f for f in listdir('img') if isfile(join('img', f))]

    images = []
    for filename in filenames:
        images.append(imageio.v2.imread(os.path.join('img', filename)))
    imageio.mimsave('information_spread.gif', images, duration=1000, format="GIF")


if __name__ == '__main__':
    random.seed(42)
    run_simulation()
    generate_gif()
