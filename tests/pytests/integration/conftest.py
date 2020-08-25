import pytest


@pytest.fixture(scope="package")
def salt_master(request, salt_factories):
    return salt_factories.spawn_master(request, "master")


@pytest.fixture(scope="package")
def salt_minion(request, salt_factories, salt_master):
    return salt_factories.spawn_minion(
        request, "minion", master_id=salt_master.config["id"]
    )


@pytest.fixture(scope="package")
def salt_call_cli(salt_factories, salt_minion):
    return salt_factories.get_salt_call_cli(salt_minion.config["id"])
