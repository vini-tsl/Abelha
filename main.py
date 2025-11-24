from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# ================= CONFIGURAÇÃO DO APP =================
app = Flask(__name__)
app.secret_key = '3j219i3n1bnu1wdh1u2dnh821kj'

# Configuração do Banco de Dados
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "beemonitor.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



from models import db
db.init_app(app)

# Importar rotas DEPOIS de inicializar o app e db
from route import *

if __name__ == "__main__":
    with app.app_context():
        # Criar diretório instance se não existir
        if not os.path.exists('instance'):
            os.makedirs('instance')
        db.create_all()
    app.run(debug=True)