from app import app
from access_keys import access_keys
app.secret_key = access_keys.flask_secret_key
app.run(debug = True, port = 8000)
