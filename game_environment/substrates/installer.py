import os
import utils
import shutil
from distutils.dir_util import copy_tree


def install_substrate(substrate_name):
    config = utils.load_config()
    substrates_suffix = "meltingpot/lua/levels/"
    source_dir = os.path.join("substrates", "lua", substrate_name)
    target_dir = os.path.join(config["meltingpot_path"].replace("~", os.path.expanduser("~")),
                              substrates_suffix, substrate_name)
    assert os.path.isdir(source_dir), "The substrate does not exist in levels/"
    if os.path.isdir(target_dir):
        print("Removing old substrate")
        shutil.rmtree(target_dir)
    copy_tree(source_dir, target_dir)
    print("Substrate installed in meltingpot!")