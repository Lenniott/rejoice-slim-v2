"""Tests for __main__.py entry point."""


def test_main_module_can_be_imported():
    """
    Test that __main__.py can be imported.

    GIVEN __main__.py
    WHEN imported
    THEN it should not raise errors
    """
    # Import should work without errors
    import rejoice.__main__  # noqa: F401


def test_main_module_has_main_function():
    """
    Test that __main__.py has a main function.

    GIVEN __main__.py
    WHEN imported
    THEN it should have a main function
    """
    from rejoice import __main__

    assert hasattr(__main__, "main")
    assert callable(__main__.main)
