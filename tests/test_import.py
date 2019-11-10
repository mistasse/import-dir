

def test_root():
    import root_external.some_package.main as x


def test_nested():
    import nested_external.external.some_package.main as x


def test_weird():
    import root_external.some_package.weird as x
