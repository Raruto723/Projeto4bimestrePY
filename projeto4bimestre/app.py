from flask import Flask
from controllers.front_controller import front_controller


app = Flask(__name__)

app.secret_key = 'chaveAWB1'

# Registra o Blueprint
app.register_blueprint(front_controller)