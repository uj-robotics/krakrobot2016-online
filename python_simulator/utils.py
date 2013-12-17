""" Utility functions """

import logging
import os
import sys
import copy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(funcName)s - %(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False
#ch_file = logging.FileHandler(os.path.join(os.path.dirname(__file__),"krakrobot_simulator.log"), )
#logger.addHandler(ch_file)
