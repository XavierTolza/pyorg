import json
from os.path import abspath, join, isfile

# Define settings
plots_folder = "img"
root_folder = "."
disable_warning = True
config_file_name = ".pyorg_config.json"
enable_figure_filename_check = False
print_line_return = True

# Search for a local config file
if isfile(config_file_name):
    with open(config_file_name, "r") as fp:
        conf = json.load(fp)
    locals().update(conf)
    pass

# Compute on those settings
root_folder = abspath(root_folder)
plots_folder = join(root_folder, plots_folder)
if disable_warning:
    import warnings

    warnings.filterwarnings("ignore")
