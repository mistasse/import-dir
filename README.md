# import-dir

When importing a directory that is not meant to be a package,
there is often the risk that it imports subdirectories as
root imports. Therefore, local folders may have conflicting
names, and one can just not copy the code from somewhere else
and import it by putting it in `sys.path`.

For instance, many people in the deep learning community provide their code as a git repository containing

- datasets
- models
- losses

directories, and then import them using "import datasets, models, ...", from anywhere in their arborescence, considering them *global* somehow. We'll therefore call those directories **falsely global** directories.

To comply with this, one can add their root directory to `sys.path`, but doing it for two projects may conflict. Therefore, the only way to circumvent conflicts is to modify all those imports to relative ones, kind of turning that code into a real package. It however requires code modification, which we may want to avoid.

This package provides an alternative way of dealing with this. It provides a way to add a custom importer for all the subdirectories of a certain package. Those subdirectories should be the **falsely global** ones. So files within those directories may refer to those when importing global packages.

Our importer will correct all the **falsely global** imports from within those directories into so as to point to the right folder.

For instance, let us consider the simple following example where we have two embedded projects that not only conflict with our arborescence, but also between each other.

```
my_project
    models
    datasets
    ...
    external
        __init__.py
        project_a
            models
                mask_rcnn.py
            datasets
                cityscapes.py
            train.py
        project_b
            models
                mask_rcnn.py
            datasets
                cityscapes.py
            scripts
                train.py
```

Every `train.py` imports its project's models and datasets packages. We would like for us to be able to import them as well for our main package. We can do so by importing `external.project_a.models` for instance, ..., but their imports must also work internally. This is where this library kicks in. `external.__init__` should customize the import routine within them so that any `import models` in `project_b` translates to `import external.project_b.models`. The same applies to `project_a`. There are some tricks to take into account, since `external.project_b.models` only creates a `external` variable, while `models` is required, but it is not really hard to make it compliant.

`external.__init__` can simply do so, by containing

```python
import sys
from import_dir import ExternalPathFinder

sys.meta_path.insert(0, ExternalPathFinder(__name__, __file__, rewrite=False))
```

Note that setting `rewrite=True` will rewrite all the files requiring an import modification irremediably, as if they were part of the root project/package, which may not be a good idea, except to get your IDE to resolve them well or to debug what `import-dir` does.
