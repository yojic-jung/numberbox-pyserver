import os
from src.util import common_util


def delete_old_file_folder():
    common_util.delete_old_files(common_util.get_resource_path() + "\\convertHwp", 'day', 1, "bak")
    common_util.delete_old_folders(common_util.get_resource_path() + "\\convertHwp", 'day', 1)
