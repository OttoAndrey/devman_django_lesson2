git pull
echo "Update backend dependencies"
source .venv/bin/activate
pip3 install -r requirements.txt
echo "Update frontend dependencies"
npm ci
echo "Update frontend"
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
echo "Update Django static"
python3 manage.py collectstatic --no-input
echo "Migrations for Django"
python3 manage.py migrate --no-input
echo "Nginx reload"
systemctl reload nginx
echo "Rollbar deploy notification"
source .env
last_commit=$(git rev-parse HEAD)
curl -H "X-Rollbar-Access-Token: $ROLLBAR_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-X POST 'https://api.rollbar.com/api/1/deploy' \
-d '{"environment": "production", "revision": "'"$last_commit"'", "rollbar_name": "Starburger", "comment": "Bash script deployment", "status": "succeeded"}'
echo "Deploy ended successfully"
