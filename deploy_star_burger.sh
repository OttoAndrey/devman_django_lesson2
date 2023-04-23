#!/bin/bash
set -e
echo "Pull project from remote repo"
git pull
echo "Update backend dependencies"
source .venv/bin/activate
pip3 install -r requirements.txt
echo "Update frontend dependencies"
npm install
echo "Update frontend"
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
echo "Update Django static"
python3 manage.py collectstatic --noinput
echo "Migrations for Django"
python3 manage.py migrate
echo "Systemd reload"
systemctl start starburger.service
echo "Deploy ended successfully"
