import logging
import os
import sys


LOG = logging.getLogger(__name__)

# add the vendor directory to the system path
HERE = os.path.dirname(__file__)
VENDOR = os.path.abspath(os.path.join(HERE, '../vendor'))

sys.path.insert(0, VENDOR)
