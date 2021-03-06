from __future__ import print_function
import os
import sys
import getopt

import pandas as pd

import main
import tools
from fspmwheat import fspmwheat_postprocessing


def run_fspmwheat(scenario_id=1, inputs_dir_path=None, outputs_dir_path=None):
    """
    Run the main.py of fspmwheat using data from a specific scenario

    :param int scenario_id: the index of the scenario to be read in the CSV file containing the list of scenarii
    :param str inputs_dir_path: the path directory of inputs
    :param str outputs_dir_path: the path to save outputs
    """

    # Path of the directory which contains the inputs of the model
    if inputs_dir_path:
        INPUTS_DIRPATH = inputs_dir_path
    else:
        INPUTS_DIRPATH = 'inputs'

    # Scenario to be run
    scenarii_df = pd.read_csv(os.path.join(INPUTS_DIRPATH, 'scenarii_list.csv'), index_col='Scenario')
    scenario = scenarii_df.loc[scenario_id].to_dict()
    scenario_name = 'Scenario_{}'.format(scenario_id)

    # Create dict of parameters for the scenario
    update_parameters = tools.buildDic(scenario)

    # Path of the directory which contains the outputs of the model
    if outputs_dir_path:
        scenario_dirpath = os.path.join(outputs_dir_path, scenario_name)
    else:
        scenario_dirpath = scenario_name

    # Create the directory of the Scenario where results will be stored
    if not os.path.exists(scenario_dirpath):
        os.mkdir(scenario_dirpath)

    # Create directory paths for graphs, outputs and postprocessings of this scenario
    scenario_graphs_dirpath = os.path.join(scenario_dirpath, 'graphs')
    if not os.path.exists(scenario_graphs_dirpath):
        os.mkdir(scenario_graphs_dirpath)
    # Outputs
    scenario_outputs_dirpath = os.path.join(scenario_dirpath, 'outputs')
    if not os.path.exists(scenario_outputs_dirpath):
        os.mkdir(scenario_outputs_dirpath)
    # Postprocessings
    scenario_postprocessing_dirpath = os.path.join(scenario_dirpath, 'postprocessing')
    if not os.path.exists(scenario_postprocessing_dirpath):
        os.mkdir(scenario_postprocessing_dirpath)

    # -- SIMULATION PARAMETERS --

    # Do run the simulation?
    RUN_SIMU = scenario.get('Run_Simulation', True)

    SIMULATION_LENGTH = scenario.get('Simulation_Length', 3000)

    # Do run the simulation from the output files ?
    RUN_FROM_OUTPUTS = scenario.get('Run_From_Outputs', False)

    # Do run the postprocessing?
    RUN_POSTPROCESSING = scenario.get('Run_Postprocessing', True)  #: TODO separate postprocessings coming from other models

    # Do generate the graphs?
    GENERATE_GRAPHS = scenario.get('Generate_Graphs', False)  #: TODO separate postprocessings coming from other models

    # Run main fspmwheat
    try:
        main.main(simulation_length=SIMULATION_LENGTH, forced_start_time=0,
                  run_simu=RUN_SIMU, run_postprocessing=RUN_POSTPROCESSING, generate_graphs=GENERATE_GRAPHS, run_from_outputs=RUN_FROM_OUTPUTS,
                  show_3Dplant=False, heterogeneous_canopy=True,
                  N_fertilizations={'constant_Conc_Nitrates': scenario.get('constant_Conc_Nitrates')},
                  PLANT_DENSITY={1: scenario.get('Plant_Density', 250.)},
                  INPUTS_DIRPATH=INPUTS_DIRPATH,
                  METEO_FILENAME=scenario.get('METEO_FILENAME'),
                  GRAPHS_DIRPATH=scenario_graphs_dirpath,
                  OUTPUTS_DIRPATH=scenario_outputs_dirpath,
                  POSTPROCESSING_DIRPATH=scenario_postprocessing_dirpath,
                  update_parameters_all_models=update_parameters)
        if RUN_POSTPROCESSING:
            fspmwheat_postprocessing.table_C_usages(scenario_postprocessing_dirpath)
            fspmwheat_postprocessing.calculate_performance_indices(scenario_postprocessing_dirpath, os.path.join(INPUTS_DIRPATH, scenario.get('METEO_FILENAME')), scenario.get('Plant_Density', 250.))

    except Exception as e:
        print(e)


if __name__ == '__main__':
    inputs = None
    outputs = None
    scenario = 1

    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:s:d", ["inputs=", "outputs=", "scenario="])
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-i", "--inputs"):
            inputs = arg
        elif opt in ("-o", "--outputs"):
            outputs = arg
        elif opt in ("-s", "--scenario"):
            scenario = int(arg)

    run_fspmwheat(inputs_dir_path=inputs, outputs_dir_path=outputs, scenario_id=scenario)
