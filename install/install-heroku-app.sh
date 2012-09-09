#!/bin/sh

echo "Downloading code from GitHub."
git clone git@github.com:honzajavorek/zitkino.git .

echo "Creating Heroku app."
heroku create

read -p "Do you wish to rename this app to 'zitkino'? [yN] " YN
while true; do
    case $YN in
        [Yy]* ) heroku apps:rename zitkino; break;;
        * ) break;;
    esac
done
heroku apps:info

echo "Creating MongoDB database."
heroku addons:add mongolab:starter

echo "Sending the code to Heroku."
git push heroku master
heroku ps:scale web=1 worker=0

echo "Creation done! Opening in browser."
heroku apps:open
