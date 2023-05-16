import os.path

from cityvillage import City, Village, CityVillageGraph
import igraph
import random
import matplotlib.pyplot as plt
import imageio
from os import listdir
from os.path import isfile, join
import glob
from pathlib import Path


def run_simulation():
    city_size = 40
    village_size = 10
    nr_villages = 5
    villages = [Village(number_nodes=village_size, name=f"village_{i}") for i in range(nr_villages)]
    city = City(number_nodes=city_size)
    graph = CityVillageGraph()
    graph = graph.add_locations(city, villages)
    colormap = {"spreading": "red", "not_interested": "blue", "ignorant": "yellow"}

    # startpoint in village
    startpoint = city_size + random.randint(0, village_size * nr_villages) - 1
    graph.vs[startpoint]['state'] = 'spreading'
    not_interested_counts = []
    spreading_counts = []
    ignorant_counts = []
    count = 0  # for naming the graph images
    while not graph.all_informed():
        plot_graph(graph, count, colormap)
        count = count + 1
        not_interested, spreading, ignorant = graph.spread_information()
        not_interested_counts.append(not_interested)
        spreading_counts.append(spreading)
        ignorant_counts.append(ignorant)
    plot_graph(graph, count, colormap)
    plot_statistics(not_interested_counts, spreading_counts, ignorant_counts)


def generate_gif():
    filenames = [f for f in listdir('img') if isfile(join('img', f))]
    filenames.sort(key=lambda x: os.path.getmtime(os.path.join("img", x)))
    images = []
    for filename in filenames:
        images.append(imageio.v2.imread(os.path.join('img', filename)))
    imageio.mimsave('information_spread.gif', images, duration=1000, format="GIF")

def plot_statistics(not_interested_counts, spreading_counts, ignorant_counts):
    plt.figure(figsize=(10, 6))
    plt.plot(ignorant_counts, label='Ignorant')
    plt.plot(spreading_counts, label='Spreading')
    plt.plot(not_interested_counts, label='Not Interested')
    plt.title('Number Of Nodes For Each State Over Time')
    plt.xlabel('Iteration')
    plt.ylabel('Number of Nodes')
    plt.legend()
    plt.grid(True)
    plt.savefig('overview_over_information_spread.png')
def plot_graph(graph, number, colormap):
    fig, ax = plt.subplots()
    node_colors = [colormap[state] for state in graph.vs['state']]
    igraph.plot(graph.get_igraph_representation(),
                bbox=(800, 800), target=ax,
                margin=50,
                vertex_label=None, edge_width=1, edge_color='black',
                vertex_color=node_colors)
    plt.savefig(f"img/graph_{number}.png")


def cleanup_directory():
    Path("img").mkdir(parents=True, exist_ok=True)
    filelist = glob.glob(os.path.join('img', "*.png"))
    for f in filelist:
        os.remove(f)


if __name__ == '__main__':
    random.seed(42)
    cleanup_directory()
    run_simulation()
    generate_gif()
