from pathlib import Path
import sys


ROOT = Path("/Users/comfan/Documents/GitHub/AIERP")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from import_vouchers import *  # noqa: F401,F403
