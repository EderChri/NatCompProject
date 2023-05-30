import os.path
from dataclasses import dataclass

import numpy as np

from cityvillage import City, Village, CityVillageGraph
import igraph
import random
import matplotlib.pyplot as plt
import imageio
from os import listdir
from os.path import isfile, join
import glob
from pathlib import Path
import sys


@dataclass
class SimSettings:
    city_size = 40
    village_size = 10
    nr_villages = 5
    spreading_prob = .3
    time_out = False
    decay = True
    spreading_time = 2
    num_startpoints = 5
    only_villages = False
    only_cities = False
    seed = 42
    connect_prob_city = 0.5
    connect_prob_vil = 0.5


def run_simulation():
    cfg = SimSettings()
    villages = [Village(number_nodes=cfg.village_size, name=f"village_{i}", prob=cfg.connect_prob_vil)
                for i in range(cfg.nr_villages)]
    city = City(number_nodes=cfg.city_size, prob=cfg.connect_prob_city)
    graph = CityVillageGraph(time_out=cfg.time_out, spreading_time=cfg.spreading_time)
    graph = graph.add_locations(city, villages)
    colormap = {"spreading": "red", "not_interested": "blue", "ignorant": "yellow"}

    # create startpoints
    startpoint_loc = []
    startpoints = []
    # make list of whether startpoints are in city or village if there are multiple points
    for i in range(cfg.num_startpoints):
        if cfg.only_villages:
            startpoint_loc.append(True)
        elif cfg.only_cities:
            startpoint_loc.append(False)
        else:
            # control that the same value is not taken all the time
            random.seed(cfg.seed + i)
            startpoint_loc.append(random.choice([True, False]))

    # get startpoints based on locations
    for i in range(cfg.num_startpoints):
        random.seed(cfg.seed + i)
        if startpoint_loc[i]:
            # WARNING make sure that the city and village size is larger than the amount of starting points
            # check if startpoint is already present
            while True:
                if (cfg.city_size + random.randint(0, cfg.village_size * cfg.nr_villages)) not in startpoints:
                    startpoints.append(cfg.city_size + random.randint(0, cfg.village_size * cfg.nr_villages))
                    break
        else:
            while True:
                if random.randint(0, cfg.city_size) not in startpoints:
                    startpoints.append(random.randint(0, cfg.city_size))
                    break

    for startpoint in startpoints:
        graph.vs[startpoint]['state'] = 'spreading'

    not_interested_counts = [0]
    spreading_counts = [cfg.num_startpoints]
    ignorant_counts = [cfg.nr_villages * cfg.village_size + cfg.city_size - cfg.num_startpoints]
    count = 0  # for naming the graph images
    not_interested = 0
    spreading = cfg.num_startpoints
    while not graph.not_spreading() and count < 30:
        plot_graph(graph, count, colormap)
        count = count + 1
        not_interested, spreading, ignorant = graph.spread_information(nr_not_interested=not_interested,
                                                                       nr_spreading=spreading,
                                                                       spread_prob=cfg.spreading_prob)
        if cfg.decay:
            cfg.spreading_prob = cfg.spreading_prob * np.exp(-0.1 * count)
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
    plt.plot(ignorant_counts, label='Ignorant', c='yellow')
    plt.plot(spreading_counts, label='Spreading', c='red')
    plt.plot(not_interested_counts, label='Not Interested', c='darkblue')
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
    plt.close()


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
