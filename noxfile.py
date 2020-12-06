"""
Run common tasks using nox.

Docs: https://nox.thea.codes/en/stable/
"""

import nox
from nox.sessions import Session

TARGETS = ("mirumon", "tests", "scripts", "noxfile.py")


@nox.session(python=False, name="format")
def run_formatters(session: Session) -> None:
    """Run all project formatters.

    Formatters to run:
    1. isort with autoflake to remove all unused imports.
    2. black for sinle style in all project.
    3. add-trailing-comma to adding or removing comma from line.
    4. isort for properly imports sorting.
    """
    # we need to run isort here, since autoflake is unable to understand unused imports
    # when they are multiline.
    # see https://github.com/myint/autoflake/issues/8
    session.run("isort", "--force-single-line-imports", *TARGETS)
    session.run(
        "autoflake",
        "--recursive",
        "--remove-all-unused-imports",
        "--remove-unused-variables",
        "--in-place",
        *TARGETS,
    )
    session.run("black", *TARGETS)
    session.run("isort", *TARGETS)


@nox.session(python=False)
def lint(session: Session) -> None:
    """Run all project linters.

    Linters to run:
    1. black for code format style.
    2. mypy for type checking.
    3. flake8 for common python code style issues.
    """
    session.run("black", "--check", "--diff", *TARGETS)
    session.run("isort", "--check-only", *TARGETS)
    session.run("mypy", *TARGETS)
    session.run("flake8", "mirumon")


@nox.session(python=False)
def test(session: Session) -> None:
    """Run pytest."""
    params = [
        "--cov-config=setup.cfg",
        "--cov=mirumon",
        "--cov=tests",
        "--cov-branch",
        "--cov-report=term-missing",
        "--cov-report=term-missing:skip-covered",
        "--no-cov-on-fail",
        "--cov-fail-under=90",
    ]
    session.run("pytest", " ".join(params))


@nox.session(python=False)
def runserver(session: Session) -> None:
    """Run pytest."""
    import uvicorn

    uvicorn.run(
        "mirumon.main:app",
        ws="websockets",
        loop="uvloop",
        http="httptools",
        workers=1,
        reload=True,
    )
