import nox


@nox.session
def lint(session: nox.Session) -> None:
    session.install("ruff", "black", "mypy")
    session.run("ruff", "check", ".")
    session.run("black", "--check", ".")
    session.run("mypy", "compiler")


@nox.session
def test(session: nox.Session) -> None:
    session.install("pytest", "pytest-cov")
    session.run("pytest")
