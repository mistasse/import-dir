"""
When importing a directory that is not meant to be a package,
there is often the risk that it imports local directories as
root imports. Therefore, local folders may have conflicting
names, and one can just not copy the code from somewhere else
and import it by putting it in sys.path.

Example: Many people in deep learning provide their code as
directory containing
- datasets
- models
- losses
directories, and then import them using "import datasets, models, ...".

We can add one's directory to the path, but doing it for two would conflict.
Therefore, the only way is to modify those imports to relative ones, and to
make that code a real package. It however requires code modification.

This package provides an alternative. One can create directories in a project
or package whose subpackages see their imports rewritten.
"""

import importlib
import sys
import os
import re

import redbaron


class ExternalPathFinder(importlib.abc.MetaPathFinder):
    def __init__(self, name, base_path, rewrite=False):
        self.name = name
        self.prefix = name+"."
        self.base_path = (os.path.dirname(base_path)
                          if base_path.endswith(".py")
                          else base_path)
        self.local_submodules = {}
        self.rewrite = rewrite

    def find_spec(self, fullname, path, target=None):
        if fullname.startswith(self.prefix):
            components = fullname[len(self.prefix):].split(".")
            root = components[0]
            if root not in self.local_submodules:
                path = os.path.join(self.base_path, root)
                self.local_submodules[root] = set([
                    item[:-3] if not is_dir and item.endswith(".py") else item
                    for item in os.listdir(path)
                    for is_dir in (os.path.isdir(os.path.join(path,item)),)
                    if is_dir or item.endswith(".py")
                ])

            spec = importlib.util.spec_from_loader(
                fullname,
                PrefixedImportSourceLoader(self.local_submodules[root], self.prefix, self.prefix+root+".",
                                           self.base_path, rewrite=self.rewrite),
                is_package=True
            )
            return spec


class PrefixedImportSourceLoader(importlib.abc.SourceLoader):
    def __init__(self, local_globals, ext_prefix, whole_prefix, base_path, rewrite):
        self.ext_prefix = ext_prefix
        self.whole_prefix = whole_prefix
        self.base_path = base_path
        self.local_globals = local_globals
        self.rewrite = rewrite

    def get_data(self, path):
        """Implementation of abstract method which when implemented should return
        the bytes for the specified path.  The path must be a str."""
        if not path.endswith(".py"):
            return ""
        ast = redbaron.RedBaron(open(path, "r").read())
        changed = False
        for node in ast.find_all("ImportNode"):
            # Iterate on imported items
            for dotted_as in list(node):
                root = dotted_as.value[0].value
                n_components = len(dotted_as.value)
                # If root is provided locally
                if root in self.local_globals:
                    # Add global prefix to local import
                    dotted_as.value[0].value = self.whole_prefix+dotted_as.value[0].value
                    if not getattr(dotted_as, "target", None):
                        # If no "as ...", add assignment of the root
                        dotted_as.insert_after(self.whole_prefix+root+" as "+root)
                        # In case this is root only, this last statement is sufficient
                        if n_components == 1:
                            dotted_as.parent.remove(dotted_as)
                    changed = True
        for node in ast.find_all("FromImportNode"):
            # If root is provided locally
            if node.value[0].value in self.local_globals:
                # Add the prefix at in the first part of the statement
                node.value[0].value = self.whole_prefix+str(node.value[0].value)
                changed = True
        code = ast.dumps()
        if self.rewrite and changed:
            open(path, "w").write(code)
        return code

    def get_filename(self, fullname):
        """Implementation of abstract method which should return the value that
        __file__ is to be set to.

        Raises ImportError if the module cannot be found.
        """
        path = os.path.join(self.base_path, *fullname[len(self.ext_prefix):].split("."))
        if os.path.isdir(path):
            init = os.path.join(path, "__init__.py")
            if os.path.exists(init):
                path = init
            else:
                path = path + "/"
        else:
            path = path + ".py"
        if not os.path.exists(path):
            raise ImportError
        return path
