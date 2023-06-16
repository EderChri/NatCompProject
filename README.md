# NatCompProject
![Alt Text](graph.gif)

This is the repository for the Natural Computing final project. The gif above 
shows an example spread of information in the graph using this repository.
This repository provides two implementations:
- Data and plot generation
- Statistical analysis

## Data and plot generation

To run the code for the data generation, run the `main.py` file. The parameters
can be set at the top of the file in the `SimSettings` as well as in the `Experiments`.
The `SimSettings` data class defines the general settings as well as the baseline
settings. For further explanation read the comments in the `SimSettings` class.

The sample data provided in this repository can be used to generate plots, by keeping
the settings as is and just changing `loadSim` to `True` in the `SimSettings`.

The `Experiments` data class can be used to change the parameters to perform 
sensitivity analysis over multiple runs. The ranges can be set for each parameter
and are then run based on ceteris paribus method, for each of the `decay` and 
`time_out` methods. 

A similar gif as the one at the top can be generated setting the `singleExperiment`
parameter to `True`. 

## Statistical analysis

To run the code for the statistical analysis the `BackupResults.zip` needs to be
extracted in the same folder as the `stat_analysis.Rmd`. Then the needed 
libraries and their dependencies need to be installed. Afterwards the code
can be run using an R IDE such as RStudio. 
Alternatively, the data for the statistical analysis can be generated by using
the `main.py` with setting the `runs` parameter in `SimSettings` to any number
higher than 1. It is highly recommended to set it to at least 5 to guarantee 
a large enough sample size. 


