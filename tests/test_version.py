from transaction import version


def test_version_constant() -> None:
    assert version.__version__ == "0.0.1"
