import time
import os
import commonUtil


def delete_old_file_folder():
    commonUtil.delete_old_files(os.getcwd() + "\\convertHwp", 'day', 1, "bak")
    commonUtil.delete_old_folders(os.getcwd() + "\\convertHwp", 'day', 1)
