from invoke import task

@task
def test(ctx):
    print("Running tests...")
    ctx.run("nosetests -v")


@task
def commit(ctx):
    message = input("Enter a git commit message:")
    print("Commiting changes...")
    ctx.run("git add . && git commit -am '{}'".format(message))


@task
def push(ctx):
    print("Pushing commit to origin master...")
    ctx.run("git push origin master")


@task(test, commit, push)
def prepare(ctx):
    print("Prep complete")

