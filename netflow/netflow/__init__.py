import logging
from os.path import join
import pathlib

# Package imports
import netflow
from netflow.network import Network 

# Create custom console logger
logging.basicConfig(
    level=logging.INFO, 
    format='[%(asctime)s] %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

# Define version
root = pathlib.Path(netflow.__file__).resolve().parent
with open(join(root, 'VERSION')) as version_file:
    __version__ = version_file.read().strip()