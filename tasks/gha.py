# -*- coding: utf-8 -*-
"""
    tasks.gha
    ~~~~~~~~~

    GitHub Actions Tasks
"""
# pylint: disable=resource-leakage
import pathlib

from invoke import task  # pylint: disable=3rd-party-module-not-gated

CODE_DIR = pathlib.Path(__file__).resolve().parent.parent
GHA_WORKFLOWS_DIR = CODE_DIR / ".github" / "workflows"
GHA_TEMPLATES_DIR = GHA_WORKFLOWS_DIR / "templates"

LINUX_DISTROS = {
    "amazon": {"display_name": "Amazon Linux", "versions": ["2"]},
    "arch": {"display_name": "Arch Linux", "versions": ["lts"]},
    "centos": {"display_name": "CentOS", "versions": ["7", "8"]},
    "debian": {"display_name": "Debian", "versions": ["9", "10"]},
    "fedora": {"display_name": "Fedora", "versions": ["31", "32"]},
    "opensuse": {"display_name": "Opensuse", "versions": ["15"]},
    "ubuntu": {"display_name": "Ubuntu", "versions": {"16.04", "18.04", "20.04"}},
}

DEFAULT_NOX_ENV = "runtests-zeromq"
DEFAULT_NOX_PASSTHROUGH_OPTS = "--ssh-tests"
LINUX_CONFIGS = {
    "": {
        "": {
            "env": DEFAULT_NOX_ENV,
            "opts": DEFAULT_NOX_PASSTHROUGH_OPTS,
            "display_name": "",
        }
    },
    "centos-7": {
        "m2crypto": {
            "env": "{}-m2crypto".format(DEFAULT_NOX_ENV),
            "opts": DEFAULT_NOX_PASSTHROUGH_OPTS,
            "display_name": "M2Crypto",
        },
        "proxy": {"env": DEFAULT_NOX_ENV, "opts": "--proxy", "display_name": "Proxy"},
        "pycryptodome": {
            "env": "{}-pycryptodome".format(DEFAULT_NOX_ENV),
            "opts": DEFAULT_NOX_PASSTHROUGH_OPTS,
            "display_name": "PyCryptodome",
        },
        "tcp": {
            "env": "runtests-tcp",
            "opts": DEFAULT_NOX_PASSTHROUGH_OPTS,
            "display_name": "TCP",
        },
    },
    "ubuntu-1604": {
        "m2crypto": {
            "env": "{}-m2crypto".format(DEFAULT_NOX_ENV),
            "opts": DEFAULT_NOX_PASSTHROUGH_OPTS,
            "display_name": "M2Crypto",
        },
        "proxy": {"env": DEFAULT_NOX_ENV, "opts": "--proxy", "display_name": "Proxy"},
        "pycryptodome": {
            "env": "{}-pycryptodome".format(DEFAULT_NOX_ENV),
            "opts": DEFAULT_NOX_PASSTHROUGH_OPTS,
            "display_name": "PyCryptodome",
        },
        "tcp": {
            "env": "runtests-tcp",
            "opts": DEFAULT_NOX_PASSTHROUGH_OPTS,
            "display_name": "TCP",
        },
    },
}


@task
def generate(ctx, output="ci", skip_windows=False, skip_macos=False):
    output_file = str(GHA_WORKFLOWS_DIR / "{}.yml".format(output))
    jobs = ""
    for template in ("pre-commit.yml", "lint.yml", "docs.yml"):
        with open(str(GHA_TEMPLATES_DIR / template)) as rfh:
            jobs += rfh.read()

    for distro, details in sorted(LINUX_DISTROS.items()):
        for version in sorted(details["versions"]):
            name = slug = "{}-{}".format(distro, version.replace(".", ""))
            display_name = "{} {}".format(details["display_name"], version.upper())
            c_details = LINUX_CONFIGS.get(slug)
            if c_details is None:
                c_details = LINUX_CONFIGS[""].copy()
            else:
                c_details.update(LINUX_CONFIGS[""].copy())
            for config, c_details in sorted(c_details.items()):
                job_name = name
                job_display_name = display_name
                if config:
                    job_name = "{}-{}".format(job_name, config)
                    if c_details["display_name"]:
                        job_display_name = "{} {}".format(
                            job_display_name, c_details["display_name"]
                        )
                nox_env_name = c_details["env"]
                nox_passthrough_opts = c_details["opts"]
                with open(str(GHA_TEMPLATES_DIR / "linux.yml")) as rfh:
                    jobs += rfh.read().format(
                        name=job_name,
                        slug=slug,
                        display_name=job_display_name,
                        nox_env_name=nox_env_name,
                        nox_passthrough_opts=nox_passthrough_opts,
                    )

    if skip_macos is False:
        with open(str(GHA_TEMPLATES_DIR / "macos.yml")) as rfh:
            jobs += rfh.read()

    if skip_windows is False:
        with open(str(GHA_TEMPLATES_DIR / "windows.yml")) as rfh:
            jobs += rfh.read()

    with open(output_file, "w") as wfh:
        with open(str(GHA_TEMPLATES_DIR / "header.yml")) as rfh:
            wfh.write(rfh.read().format(workflow=output, jobs=jobs))
