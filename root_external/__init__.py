import sys
from import_dir import ExternalPathFinder

sys.meta_path.insert(0, ExternalPathFinder(__name__, __file__, rewrite=False))
