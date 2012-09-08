
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
