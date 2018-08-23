# Std
import glob
import shutil  # para borrar el tempdir
import tempfile  # para crear el tempdir
import unittest
from io import StringIO
import pandas
import os
import re

# Mine
import running.simulation_run_info as simu_run_info
from running.sweep import ParametersSweepResults
from plotting.plot_sweep import SweepPlot


class TestSweepPlot(unittest.TestCase):
    # setup y teardown de los tests
    def setUp(self):
        # Create tempdir and save its path
        self._temp_dir = tempfile.mkdtemp()
        self._temp_files = []  # each test case can create individual files

    def tearDown(self):
        pass
        shutil.rmtree(self._temp_dir)
        for f in self._temp_files:
            f.close()

    # Tests:
    def test_plot_sweep_creates_files_in_folder(self):
        # Create an example sweep
        sweep_specs, var_name = self.sweepExample()
        # Initialize sweep plotter
        sweep_plotter = SweepPlot(sweep_specs)
        # Plot sweep specs to temp folder
        sweep_plotter.plotInFolder(var_name, self._temp_dir)
        # Get plots extensions regex
        regex = '.*\.(png|svg)$'
        # Get list of files from regex
        files_in_dir = os.listdir(self._temp_dir)
        plot_files = [x for x in files_in_dir if re.match(regex, x)]
        # Check that there is at least one plot
        if len(plot_files) < 1:
            error_msg = "The plot function should create at least one plot file in the destination folder."
            self.fail(error_msg)


    # Auxs:
    def sweepExample(self):
        # Generate dataframe
        df_std_run = pandas.read_csv(StringIO(bb_std_run_str), index_col=0)
        model_name = "BouncingBall"
        std_run = simu_run_info.SimulationSpecs(StringIO(bb_std_run_str), {}, model_name, "/path/to/exe")
        # Simulate perturbations by multiplying variables
        perturbed_runs = []
        for i in range(1, 9):
            df_perturbed_i = df_std_run.copy()
            df_perturbed_i["v"] = df_perturbed_i.apply(lambda row: row["v"] * (1 + i / 8), axis=1)
            run_output_name = "run_{0}.csv".format(i)
            run_output_path = os.path.join(self._temp_dir, run_output_name)
            df_perturbed_i.to_csv(run_output_path)
            # Pretend that e is always changed to 1 and g is swept in each run
            run_parameters_changed = {
                "e": 1,
                "g": i,
            }
            swept_param_info = simu_run_info.PerturbedParameterInfo("g", 0, i)
            swept_params_info_list = [swept_param_info]
            # The executable can be anything as we asume it has already been ran
            run_executable = "/path/to/exe"
            simu_specs = simu_run_info.SweepSimulationSpecs(run_output_path, run_parameters_changed, model_name,
                                                            run_executable, swept_params_info_list)
            perturbed_runs.append(simu_specs)
        sweep_params_swept = ["g"]
        sweep_params_fixed = [simu_run_info.PerturbedParameterInfo("e", 0, 1)]
        sweep_specs = ParametersSweepResults(model_name, sweep_params_swept, sweep_params_fixed, std_run,
                                             perturbed_runs)
        # Var to analyze
        var_name = "h"
        # Returns sweep example objects
        return sweep_specs, var_name


###########
# Globals #
###########
bb_std_run_str = \
    """"time","h","v","der(h)","der(v)","v_new","flying","impact"
    0,1,0,0,-9.81,0,1,0
    1,0.2250597607429705,-2.279940238910565,-2.279940238910565,-9.81,3.100612842801532,1,0
    2,0.04243354772647411,-0.5463586255141026,-0.5463586255141026,-9.81,1.063510205007515,1,0
    3,2.101988323055078e-11,0,0,0,0,0,1"""
