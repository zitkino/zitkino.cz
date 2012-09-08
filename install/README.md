
# Installation scripts

To install master heroku app, follow this:

    mkdir zitkino
    cd zitkino
    wget https://raw.github.com/honzajavorek/zitkino/master/install/install-heroku-app.sh
    chmod -x install-heroku-app.sh
    ./install-heroku-app.sh

To install scheduler heroku app, follow this:

    mkdir zitkino-cron
    cd zitkino-cron
    wget https://raw.github.com/honzajavorek/zitkino/master/install/install-heroku-scheduler-app.sh
    chmod -x install-heroku-scheduler-app.sh
    ./install-heroku-scheduler-app.sh

Both scripts also pull code from this git repository. They don't install Heroku toolbelt into your system and they assume you already performed `heroku login`. They don't install `zitkino` python package into your environment, they just pull the code from GitHub and setup corresponding Heroku apps including the scheduler.

## Tip

You could add something like this to your master app's `.git/config`:

    [remote "heroku-cron"]
        url = git@heroku.com:zitkino-cron.git
        fetch = +refs/heads/*:refs/remotes/heroku-cron/*

Then you don't need to maintain two redundant projects on your disk and you deploy to production by:

    git push heroku master
    git push heroku-cron master

Or, better with `fabric`:

    fab deploy

Fabric script automatically deploys to all remotes starting with `heroku`.
