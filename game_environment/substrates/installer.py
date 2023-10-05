import os
import shutil
import logging
from distutils.dir_util import copy_tree
import game_environment.utils as utils

logger = logging.getLogger(__name__)

def install_substrate(substrate_name):
    config = utils.load_config()
    meltingpot_dir = os.getenv("MELTING_POT_DIR")
    substrates_suffix = "meltingpot/lua/levels/"
    source_dir = os.path.join(config["game_folder"], "substrates", "lua", substrate_name)
    target_dir = os.path.join(meltingpot_dir.replace("~", os.path.expanduser("~")),
                              substrates_suffix, substrate_name)
    assert os.path.isdir(source_dir), "The substrate does not exist in levels/"
    if os.path.isdir(target_dir):
        logger.debug("Removing old substrate")
        shutil.rmtree(target_dir)
    copy_tree(source_dir, target_dir)
    logger.debug("Substrate installed in meltingpot!")