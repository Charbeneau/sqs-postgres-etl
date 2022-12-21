from pytest import fixture


@fixture
def global_fixture():
    print("\n(Doing global fixture setup stuff!)")