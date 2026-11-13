"""pytest fixtures shared by all test files.

pytest loads this file automatically. A test asks for a fixture by naming it
as an argument, e.g. ``def test_x(device): ...``.
"""
import pytest

from helpers import SETTINGS, make


@pytest.fixture
def device():
    """Device on 1.0 (slot A), 2.0 offered as an optional update, no faults."""
    return make()


@pytest.fixture(params=[False, True], ids=["optional", "mandatory"])
def any_update_device(request):
    """Same as ``device``, but the test runs twice: optional and mandatory update."""
    return make(mandatory=request.param)


@pytest.fixture
def user_settings():
    """The settings every test device starts with."""
    return dict(SETTINGS)
