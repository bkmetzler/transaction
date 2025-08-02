import nox
from nox.sessions import Session


@nox.session(python=["3.12"])
def tests(session: Session) -> None:
    session.install(".[dev]")
    session.run("pytest")


@nox.session
def lint(session: Session) -> None:
    session.install("black", "mypy", "ruff")
    session.run("black", "--check", "--diff", ".")
    session.run("mypy", "-p", "transaction")
    session.run("ruff", "check", ".")


@nox.session
def mypy(session: Session) -> None:
    session.install("mypy")
    session.run("mypy", "-p", "transaction")


@nox.session
def black(session: Session) -> None:
    session.install("black")
    session.run("black", ".")


@nox.session
def ruff(session: Session) -> None:
    session.install("ruff")
    session.run("ruff", "format", ".")


@nox.session
def format(session: Session) -> None:
    ruff(session)
    black(session)
