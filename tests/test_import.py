import nodeps


def test_import() -> None:
    """Test that the package can be imported."""
    assert isinstance(nodeps.__name__, str)
