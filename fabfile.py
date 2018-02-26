from fabric.api import local, settings, abort
from fabric.contrib.console import confirm

def test():
    with settings(warn_only=True):
        result = local("nosetests -v", capture=True)
    if result.failed and not confirm("Tests failed. Continue?"):
        abort("Aborted at user request.")


def pull():
    local("git pull origin master")


def heroku_push():
    local("git push heroku master")


def heroku_test():
    local("heroku run nosetests -v")


def deploy():
    test()
    heroku_push()
    heroku_test()


def rollback():
    local("heroku rollback")
