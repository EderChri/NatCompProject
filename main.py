import os.path
from dataclasses import dataclass

import numpy as np

from cityvillage import Dwelling, CityVillageGraph
import igraph
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import imageio
from os import listdir
from os.path import isfile, join
import glob
from pathlib import Path
import copy
import tqdm
import pandas as pd


@dataclass
class SimSettings:
    """
    Data class used for the general settings of the simulation
    Here the baseline parameter should be set
    """
    city_size = 40  # Number of nodes in the city
    village_size = 10  # Number of nodes in the villages
    nr_villages = 5  # Number of villages
    spreading_prob = .8  # Baseline spreading probability
    time_out = False  # Set to True to use the time_out method for spreading
    decay = True  # Set to True to use the decay method for spreading
    spreading_time = 2  # Only relevant if time_out set to True, number of iterations a node spreads information
    num_start_points = 1  # Number of starting points (baseline)
    only_villages = True  # If True, starting points are only spawned in villages
    only_cities = False  # If True, starting points are only spawned in the city
    seed = 60  # random seed for simulation
    connect_prob_city = 0.5  # Probability of city nodes connected with each other
    connect_prob_vil = 0.5  # Probability of villages nodes connected with each other
    decay_param = -0.025  # Parameter for the decrease of the spreading_probability, only used when decay True
    loadSim = False  # If True, just load the already calculated data and produce plots
    runs = 1  # Number of runs to perform, if > 1 plotting will be disabled


@dataclass
class Experiments:
    """
    Data class for the parameter ranges run through in the experiments
    """

    singleExperiment = False  # If True only run one experiment
    decay = [True, False]
    time_out = [False, True]
    spreading_method = [decay, time_out]
    spreading_method_names = ['decay', 'timeout']

    spreading_prob = [0.15, 0.3, 0.6, 0.8, 0.9]
    spreading_time = [0, 1, 2, 5, 10]
    connect_prob_city = [0.1, 0.25, 0.5, 0.75, 1]
    connect_prob_vil = [0.1, 0.25, 0.5, 0.75, 1]
    parameters = [spreading_prob, spreading_time, connect_prob_city, connect_prob_vil]
    parameter_names = ["spreading_prob", "spreading_time", "connect_prob_city", "connect_prob_vil"]

    num_start_points = [1, 5]
    only_villages = [True, False]
    only_cities = [True, False]
    # vector representation situation [num_start, only_vil, only_cit]
    situation1 = [0, 0, 1]  # 1 start village
    situation2 = [0, 1, 0]  # 1 start city
    situation3 = [1, 0, 1]  # 5 start village
    situation4 = [1, 1, 0]  # 5 start city
    situation5 = [1, 1, 1]  # 5 start combined
    situations = [situation1, situation2, situation3, situation4, situation5]
    situation_name = ["Village", "City", "MultVillage", "MultCity", "MultVillage&City"]


def run_simulation(config: SimSettings, plot=False):
    """
    Main class for the simulation. Performs one run of the simulation given the parameter
    :param config: SimSettings object that determines all parameters of the simulation
    :param plot: Boolean that defines whether the run should be plotted or not
    :return:
    """
    # Create villages, city and the graph
    villages = [Dwelling(number_nodes=config.village_size, prob=config.connect_prob_vil)
                for _ in range(config.nr_villages)]
    city = Dwelling(number_nodes=config.city_size, prob=config.connect_prob_city)
    graph = CityVillageGraph(time_out=config.time_out, spreading_time=config.spreading_time)
    graph = graph.add_dwellings(city, villages)
    # Defines colormap for nodes in plot
    colormap = {"spreading": "red", "not_interested": "blue", "ignorant": "yellow"}

    # create start_points
    startpoint_loc = []
    start_points = []
    # make list of whether start_points are in city or village if there are multiple points
    for i in range(config.num_start_points):
        if config.only_villages:
            startpoint_loc.append(True)
        elif config.only_cities:
            startpoint_loc.append(False)
        else:
            # control that the same value is not taken all the time
            np.random.seed(config.seed + i)
            startpoint_loc.append(np.random.choice([True, False]))

    # get start_points based on locations
    for i in range(config.num_start_points):
        np.random.seed(config.seed + i)
        if startpoint_loc[i]:
            # WARNING make sure that the city and village size is larger than the amount of starting points
            # check if startpoint is already present
            while True:
                if (config.city_size + np.random.randint(0,
                                                         config.village_size * config.nr_villages)) not in start_points:
                    start_points.append(
                        config.city_size + np.random.randint(0, config.village_size * config.nr_villages))
                    break
        else:
            while True:
                if np.random.randint(0, config.city_size) not in start_points:
                    start_points.append(np.random.randint(0, config.city_size))
                    break

    for startpoint in start_points:
        graph.vs[startpoint]['state'] = 'spreading'

    # used for counting nodes of different states
    not_interested_counts = [0]
    spreading_counts = [config.num_start_points]
    ignorant_counts = [config.nr_villages * config.village_size + config.city_size - config.num_start_points]
    # Defines the number of iterations
    count = 0
    not_interested = 0
    spreading = config.num_start_points
    spreading_prob = config.spreading_prob
    while not graph.not_spreading() and count < 30:
        plot_graph(graph, count, colormap)
        count = count + 1
        not_interested, spreading, ignorant = graph.spread_information(nr_not_interested=not_interested,
                                                                       nr_spreading=spreading,
                                                                       spread_prob=spreading_prob)
        if config.decay:
            spreading_prob = spreading_prob * np.exp(config.decay_param * count)
        not_interested_counts.append(not_interested)
        spreading_counts.append(spreading)
        ignorant_counts.append(ignorant)

    if plot:
        plot_graph(graph, count, colormap)
        plot_statistics(not_interested_counts, spreading_counts, ignorant_counts)
    return count


def generate_gif():
    """
    Generates a gif out of the images in the img dir
    :return:
    """
    filenames = [f for f in listdir('img') if isfile(join('img', f))]
    filenames.sort(key=lambda x: os.path.getmtime(os.path.join("img", x)))
    images = []
    for filename in filenames:
        images.append(imageio.v2.imread(os.path.join('img', filename)))
    imageio.mimsave('information_spread.gif', images, duration=1000, format="GIF", loop=0)


def plot_statistics(not_interested_counts, spreading_counts, ignorant_counts):
    """
    Plots the number of nodes of certain states against iterations
    :param not_interested_counts: List of nodes in the not_interested state at given iteration
    :param spreading_counts: List of nodes in the spreading state at given iteration
    :param ignorant_counts: List of nodes in the ignorant state at given iteration
    :return:
    """
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
    """
    Generates a plot of the cityvillage graph
    :param graph: CityVillageGraph object to be plotted
    :param number: Int indicating the iteration, used for naming
    :param colormap: Dictionary indicating colour for each node
    :return:
    """
    fig, ax = plt.subplots()
    node_colors = [colormap[state] for state in graph.vs['state']]
    igraph.plot(graph.get_igraph_representation(),
                bbox=(800, 800), target=ax,
                margin=50,
                vertex_label=None, edge_width=1, edge_color='black',
                vertex_color=node_colors)
    plt.savefig(f"img/graph_{number}.png")
    plt.close()


def plot_boxplot(df, parameter_name, spreading_method_name):
    """
    Plots a boxplot of a given spreading_method
    :param df: dataset containing the data to plot
    :param parameter_name: name of the spreading parameter that was varied
    :param spreading_method_name: name of the used spreading_method
    :return:
    """
    df.boxplot(column="time", by="situation")

    plt.title(f'Sensitivity analysis of parameter {parameter_name} with spreading method {spreading_method_name}')
    plt.xlabel('Startpoint')
    plt.ylabel('Time')
    check_create_dir("sensitivity")
    plt.savefig(f"sensitivity/{parameter_name}_{spreading_method_name}.png")
    plt.close()


def plot_scatterplot(df, parameter_name, spreading_method_name, situation_name):
    """
    Function to plot a scatter plot of experiment results of a parameter variation
    Jitters points if they are on top of each other
    :param df: dataset containing the simulation data
    :param parameter_name: parameter that was varied in experiment
    :param spreading_method_name: spreading method used in the experiment
    :param situation_name: list of situations that were covered
    :return:
    """
    df.situation = pd.Categorical(df.situation, categories=situation_name, ordered=True)
    groups = df.groupby(['situation'])

    fig, ax = plt.subplots(figsize=(8, 6))
    colormap = plt.colormaps.get_cmap("tab10")
    unique_param_values = np.sort(df[parameter_name].unique())

    for i, (situation, group_data) in enumerate(groups):
        # Save the point coordinates to know if they would be plotted on top of each other
        point_coordinates = set()
        for j, row in group_data.iterrows():
            unique_index = np.argwhere(unique_param_values == row[parameter_name])[0][0]
            color = colormap(
                unique_index % colormap.N)
            x = i
            y = row['time']
            coordinate = (x, y)

            # If point already there, add jitter
            if coordinate in point_coordinates:
                offset = np.random.uniform(-0.1, 0.1)
                x += offset

            point_coordinates.add((x, y))
            ax.scatter(x, y, color=color)

    unique_param_values = df[parameter_name].unique()
    legend_elements = [
        mpatches.Patch(color=colormap(i % colormap.N), label=f'{parameter_name} = {val}')
        for i, val in enumerate(unique_param_values)
    ]
    plt.legend(handles=legend_elements, loc="best", title=f"Color legend for {parameter_name}")

    ax.set_xticks(np.arange(len(groups)))
    ax.set_xticklabels([k[0] for k, _ in groups])
    plt.title(f'Sensitivity analysis of parameter {parameter_name} with spreading method {spreading_method_name}')
    plt.xlabel('Situation')
    plt.ylabel('Time')
    plt.ylim((0, 32))
    plt.savefig(f"sensitivity/{parameter_name}_{spreading_method_name}_scatter.png")
    plt.close()


def check_create_dir(name):
    """
    Function to check whether a directory exists, and if it doesn't create it
    :param name: name of the directory
    :return:
    """
    exists = os.path.exists(name)
    if not exists:
        os.makedirs(name)
        print(f"The {name} directory is created!")


def cleanup_directory(cfg):
    """
    Function that removes all png from the img folder
    :return:
    """
    Path("img").mkdir(parents=True, exist_ok=True)
    filelist = glob.glob(os.path.join('img', "*.png"))
    for f in filelist:
        os.remove(f)

    Path("sensitivity").mkdir(parents=True, exist_ok=True)
    filelist = glob.glob(os.path.join('sensitivity', "*.png"))
    for f in filelist:
        os.remove(f)

    Path("csv").mkdir(parents=True, exist_ok=True)
    filelist = glob.glob(os.path.join(f"csv/{str(cfg.seed)}", "*.csv"))
    for f in filelist:
        os.remove(f)


def get_row_dict(config, time, situation):
    """
    Helper function to generate a dictionary row
    :param config: SimSettings object containing all the parameter
    :param time: Int indicating the iteration
    :return: Dictionary used for pandas DataFrame generation
    """
    row = {"time": time, "situation": situation, "spreading_prob": config.spreading_prob, "time_out": config.time_out,
           "decay": config.decay,
           "connect_prob_city": config.connect_prob_city, "connect_prob_vil": config.connect_prob_vil,
           "num_start_points": config.num_start_points, "only_cities": config.only_cities,
           "only_villages": config.only_villages, "spreading_time": config.spreading_time}
    return row


def sim_wrapper(config, return_list, change_parameter, param_name, situation):
    """
    Wrapper function, that runs the simulation using the given experiment parameters
    :param config: SimSettings object that contains the baseline parameters
    :param return_list: List of dictionaries used for pandas DataFrame generation
    :param change_parameter: List of values for the parameter that is varied in this experiment
    :param param_name: String containing the name of the parameter to be varied in this experiment
    :return: List of dictionaries with the outcome of this experiment added
    """
    sim_cfg = copy.deepcopy(config)
    for param in tqdm.tqdm(change_parameter):
        setattr(sim_cfg, param_name, param)
        time = run_simulation(sim_cfg)
        return_list.append(get_row_dict(sim_cfg, time, situation))
    return return_list


def print_header(header):
    """
    Short helper function to print nice header output
    :param header: String that is to be printed with a header
    :return:
    """
    print('-' * 50)
    print(header)


if __name__ == '__main__':
    sim_list = []
    cfg = SimSettings()
    exp = Experiments()
    if not cfg.loadSim:
        cleanup_directory(cfg)
    np.random.seed(cfg.seed)

    if exp.singleExperiment:
        run_simulation(cfg, plot=True)
        generate_gif()
    else:
        check_create_dir(f"csv")
        for param in range(len(exp.parameters)):
            # Run all the settings for all different numbers of starting points
            for nr_spreading_methods in range(len(exp.spreading_method)):
                sim_list = []
                if cfg.runs != 1:
                    plotting = False
                else:
                    plotting = True
                if not cfg.loadSim:
                    for run in range(cfg.runs):
                        print(run)
                        for situation_nr in range(len(exp.situations)):
                            cfg.decay = exp.decay[nr_spreading_methods]
                            cfg.time_out = exp.time_out[nr_spreading_methods]
                            spreading_method_name = exp.spreading_method_names[nr_spreading_methods]

                            parameter = exp.parameters[param]
                            parameter_name = exp.parameter_names[param]

                            situation_name = exp.situation_name[situation_nr]

                            print('=' * 50)
                            print(f'Situation: {situation_name}; Parameter:{parameter_name}')

                            # Run for combination start in cities and villages
                            cfg.num_start_points = exp.num_start_points[exp.situations[situation_nr][0]]
                            cfg.only_villages = exp.only_villages[exp.situations[situation_nr][1]]
                            cfg.only_cities = exp.only_cities[exp.situations[situation_nr][2]]

                            sim_list = sim_wrapper(cfg, sim_list, parameter, parameter_name, situation_name)

                            if plotting:
                                df = pd.DataFrame(sim_list)
                                plot_boxplot(df, parameter_name, spreading_method_name)
                                plot_scatterplot(df, parameter_name, spreading_method_name, exp.situation_name)

                    df = pd.DataFrame(sim_list)
                    check_create_dir(f"csv/{str(cfg.seed)}")
                    df.to_csv(f"csv/{cfg.seed}/{parameter_name}_{spreading_method_name}.csv", index=False)

                else:
                    parameter_name = exp.parameter_names[param]
                    spreading_method_name = exp.spreading_method_names[nr_spreading_methods]
                    df = pd.read_csv(f"csv/{cfg.seed}/{parameter_name}_{spreading_method_name}.csv")
                    plot_scatterplot(df, parameter_name, spreading_method_name, exp.situation_name)
