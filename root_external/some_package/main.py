import submodule, other_submodule.deep

assert submodule.name == "root_external"
assert other_submodule.deep.name == "deep"

from submodule import name as root_name
from other_submodule import deep
from other_submodule.deep import name as deep_name, name as deep_n

assert deep.name == "deep" == deep_name == deep_n
assert root_name == "root_external"
