#!/bin/sh

echo "Downloading code from GitHub."
git clone git@github.com:honzajavorek/zitkino.git .

echo "Creating Heroku app."
heroku create

read -p "Do you wish to rename this new app to 'zitkino-cron'? [yN] " YN
while true; do
    case $YN in
        [Yy]* ) heroku apps:rename zitkino-cron; break;;
        * ) break;;
    esac
done
heroku apps:info

echo "Connecting this app to MongoDB database of your master app."
read -p "Is your master app called 'zitkino'? [yN] " YN
APP_NAME=""
while true; do
    case $YN in
        [Yy]* ) APP_NAME="zitkino"; break;;
        * ) echo "Please, enter a name of your master app: "; read APP_NAME; break;;
    esac
done
DATABASE_URL=$(heroku config --app "$APP_NAME" | grep MONGOLAB_URI | sed 's/MONGOLAB_URI: \+//') && heroku config:add MONGOLAB_URI="$DATABASE_URL"
heroku config

echo "Setting up scheduler."
heroku addons:add scheduler:standard
echo "Now a web page with scheduler settings will be opened. Create a new record like this:"
echo
echo "worker    Daily    22:00 UTC"
echo "(22:00 UTC should be midnight in Czech Republic)"
echo
read -p "Okay? " WHATEVER
echo "Opening a browser..."
heroku addons:open scheduler
read -p "Are you done? " WHATEVER

echo "Sending the code to Heroku."
git push heroku master
heroku ps:scale web=0 worker=0

echo "Creation done!"
