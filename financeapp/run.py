import os
from flask import Flask
from home import home_bp
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


app.register_blueprint(home_bp, url_prefix='')

if __name__ == '__main__':
    app.run(debug=True)
