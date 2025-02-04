from flask import flash, request
from uuid import uuid4
import os
import json
import config

#-- Funções para manipular arquivos
def load_data():
    if not os.path.exists(config.DATA_FILE):
        return [ ]
    with open(config.DATA_FILE, "r") as file:
        return (json.load(file))

#--------------------------------------------
def load_dados():
    if not os.path.exists(config.DADOS_FILE):
        return [ ]
    with open(config.DADOS_FILE, "r") as file:
        return (json.load(file))

#--------------------------------------------
def save_data(data):
    with open(config.DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

#--------------------------------------------
def save_dados(dados):
    with open(config.DADOS_FILE, "w") as file:
        json.dump(dados, file, indent=4)

#--------------------------------------------
def verificarArquivos(imagem):
	return ('.' in imagem.filename and imagem.filename.rsplit('.', 1)[1].lower() in config.TIPOS_IMAGEM)

#------------------------------------------------------------------------
def upload_imagem(imagem):    
    # Garante que a pasta de upload exista
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True) #garante que o diretório upload existe ou, caso contrário, ele é criado

    if (imagem.filename == ''):
        
        return 'uploads/image/perfil.png'

    elif (not verificarArquivos(imagem)):

        return 'uploads/image/perfil.png'
    else:
        # Gera um nome ÚNICO para a imagem e salva no diretório de uploads
        filename = f"{uuid4()}.{imagem.filename.rsplit('.', 1)[1].lower()}"
        filepath = os.path.join(config.UPLOAD_FOLDER, filename)
        imagem.save(filepath)
        flash("Imagem enviada com sucesso!")
        return 'uploads/image/' + filename
#----------------------------------------------------------------------------------------------------

def cadastro_biblioteca(login,senha,image):
    bibliotecaCadastro = load_data()
    condi = True
    for item in bibliotecaCadastro:
        if login in item['login']:
            condi = False
        
    if condi:
        photo = upload_imagem(image)
        add = {'login':login,
                'senha':senha,
                'photo':photo}
        bibliotecaCadastro.append(add)
        save_data(bibliotecaCadastro)
        flash(request.form.get('textEmail') + " cadastrado com sucesso!")
        return True
    else:
        flash("Erro de cadastro. Nome de usuário já em uso.")
        return False
#------------------------------------------------------------------  
def favoritos(dados,usuario):
    data = load_dados()
    data.append({'id':usuario, 'favoritos':dados})
    save_dados(data)

#---------------------------------------------------------------
def rmv_favorite(id,nome):
    dados = load_dados()
    novo_dados = []
    for i in dados:
        if not(i['id'] == id and i['favoritos']['titulo'] == nome):
            novo_dados.append(i)

    save_dados(novo_dados)
#--------------------------------------------------------------------
def atualizarSenha(nome,senha):
    data = load_data()
    novo_data = []
    for i in data:
        if not(i['login'] == nome):
            novo_data.append(i)
        else:
            foto = i['photo']
    loginConfig = {
        'login' : nome,
        'senha' : senha,
        'photo' : foto
    }
    novo_data.append(loginConfig)
    save_data(novo_data)