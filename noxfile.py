import nox
from nox.sessions import Session

PYTHON_39 = "3.9"
PYTHON_310 = "3.10"
PYTHON_311 = "3.11"
PYTHON_312 = "3.12"
PYTHON_313 = "3.13"
PYTHON_314 = "3.14"


PYTHON_VERSIONS = {
    "all": [PYTHON_311, PYTHON_312, PYTHON_313, PYTHON_314],
    "standard": [PYTHON_311, PYTHON_312, PYTHON_313],
    "latest": [PYTHON_312],
}


@nox.session(python=PYTHON_VERSIONS["standard"])
def tests(session: Session) -> None:
    """
    Initialize environment and run pytest

    Args:
        session: nox.session.Session

    Returns:
        None
    """
    session.install(".[dev]")
    session.run("pytest")


@nox.session(python=PYTHON_VERSIONS["standard"])
def lint(session: Session) -> None:
    """
    Initialize environment by installing black, mypy, and ruff.
    Runs associated commands

    Args:
        session: nox.session.Session

    Returns:
        None
    """

    session.install("black", "mypy", "ruff")
    session.run("black", "--check", "--diff", ".")
    session.run("mypy", "-p", "transaction")
    session.run("ruff", "check", ".")


@nox.session(python=PYTHON_VERSIONS["standard"])
def mypy(session: Session) -> None:
    """
    Initialize environment and run mypy

    Args:
        session: nox.session.Session

    Returns:
        None
    """
    session.install("mypy")
    session.run("mypy", "-p", "transaction")


@nox.session(python=PYTHON_VERSIONS["latest"])
def black(session: Session) -> None:
    """
    Initialize environment and run black to reformat code

    Args:
        session: nox.session.Session

    Returns:
        None
    """

    session.install("black")
    session.run("black", ".")


@nox.session(python=PYTHON_VERSIONS["latest"])
def ruff(session: Session) -> None:
    """
    Initialize environment, install and run ruff to reformat code

    Args:
        session: nox.session.Session

    Returns:
        None
    """
    session.install("ruff")
    session.run("ruff", "format", ".")


@nox.session(default=False)
def format(session: Session) -> None:
    """
    Initialize environment and run ruff and black sessions

    Args:
        session: nox.session.Session

    Returns:
        None
    """
    ruff(session)
    black(session)
