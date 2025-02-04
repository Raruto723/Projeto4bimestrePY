from  flask import render_template, url_for, request, redirect, session, flash, Blueprint, make_response
from requests import get
from models.data_manager import cadastro_biblioteca, load_data, favoritos,load_dados,rmv_favorite,atualizarSenha

front_controller = Blueprint('front_controller', __name__)

@front_controller.before_request
def before_request() :
    if 'usuarioLogado' not in session:
        usuario_cookie = request.cookies.get("usuarioLogado")
        if usuario_cookie != None and usuario_cookie != '':
            session["usuarioLogado"] = usuario_cookie

#---------------- Rota PRINCIPAL ----------------------------#
@front_controller.route('/')
def principal( ):
        foto = load_data()
        return render_template('principal.html', foto = foto)
#---------------- Rota LOGIN ----------------------------#
@front_controller.route('/login')
def login():
    if session.get('usuarioLogado'):
        return(redirect(url_for('front_controller.principal')))
    else:
        return render_template("login.html")

#------------------------ Rota cadastro ------------------------
@front_controller.route('/cadastro')
def cadastro():
    foto = load_data()
    return render_template('cadastro.html',  foto = foto)

#------------------------ Rota FazerCadastro ------------------------
@front_controller.route('/FazerCadastro', methods=["GET", "POST"])
def FazerCadastro():
    if request.method == "POST" :

        login = request.form.get('textEmail')
        senha = request.form.get('textSenha')
        image = request.files.get('fileFoto')
        if cadastro_biblioteca(login,senha,image):
            return redirect(url_for('front_controller.login'))
        else:
            return redirect(url_for('front_controller.cadastro'))
    else:
        return(redirect(url_for('front_controller.principal')))


#---------------- Rota para AUTENTICAÇÃO ----------------------------#
@front_controller.route('/autenticar', methods=["GET", "POST"])
def autenticar():
    if(request.method == "POST"):
        dados = load_data()
        cond = 0
        for i in dados:
            if i['login'] == request.form.get('textEmail') and i['senha'] == request.form.get('textSenha'):
                cond = 1
            
        if cond == 1:
            #------------Inicia a sessão do usuário com o e-mail dele ----------#
            session['usuarioLogado'] = request.form.get('textEmail')
            flash(request.form.get('textEmail') + " logado com sucesso!")

            lembrar = request.form.get("lembrar")
            if lembrar:
                resp = make_response(redirect(url_for('front_controller.biblioteca')))
                resp.set_cookie("usuarioLogado", request.form.get('textEmail') , max_age=60*60*24*30)  # Cookie expira em 30 dias
                return resp

            return(redirect(url_for('front_controller.biblioteca')))
            
        flash("Confira seu usuário e/ou senha. Erro de login")
        session.pop('usuarioLogado', None)
        return redirect(url_for('front_controller.login'))
    
    else:
        return redirect(url_for('front_controller.login'))

#---------------- Rota Biblioteca ----------------------------#
@front_controller.route('/biblioteca', methods=["GET", "POST"])
def biblioteca():

    dados={'results':[]}
    if 'usuarioLogado' not in session:
        return(redirect(url_for('front_controller.principal')))
    else:
            
        #Passo 2. recuperar a URL da API a ser usada
        api_url = 'https://api.themoviedb.org/3/discover/movie?language=pt-BR&page=1&with_genres=14&api_key=1671d24398a298a717bedcb75253483f'
        
        #Passo 3. fazer uma requisição GET para a API
        resposta = get(api_url)

        #Passo 4. verifica se a requisição foi bem-sucedida (status 200)
        if (resposta.status_code == 200):
            #Passo 5. converte a resposta JSON para um dicionário Python
            dados = resposta.json( ) 
        else:
            dados = {"error": "Não foi possível sobter os dados"}

        foto = load_data()
        return render_template('biblioteca.html', dados = dados['results'], foto = foto)
                # O arquivo JSON nem sempre está no formato que precisamos. 

#------------------- Rota favorite -----------------------------------------
@front_controller.route('/favorite')
def favorite():
    foto = load_data()
    dados = load_dados()
    return render_template('favorite.html',foto = foto, dados = dados)

#--------------------- Rota favoritar --------------------------------
@front_controller.route('/favoritar',methods=["GET", "POST"])
def favoritar():
    if request.method == "POST":
        dados = {
            'titulo': request.form.get('titulo'),
            'overview': request.form.get('overview'),
            'backdrop_path': request.form.get('backdrop_path'),
        }
        usuario = session.get('usuarioLogado')
        favoritos(dados,usuario)
    return redirect(url_for('front_controller.biblioteca'))
#------------------------- Rota para remover item dos favoritos ----------------------------------
@front_controller.route('/remove', methods=["GET", "POST"])
def remove():
    if request.method == "POST":
        id = request.form.get('id')
        nome = request.form.get('nome')
        rmv_favorite(id,nome)
        flash("Filme removido com sucesso.")
        return redirect(url_for('front_controller.favorite'))
    else:
        return redirect(url_for('front_controller.principal'))
#----------------- Atualizar -------------------
@front_controller.route('/atualizar')
def atualizar():
    foto = load_data()
    return render_template('atualizarCadastro.html', foto = foto)

#--------------------- AtualizarCadastro --------------------------
@front_controller.route('/atualizarCadastro', methods=["GET", "POST"])
def atualizarCadastro():
    nome = session.get('usuarioLogado')
    novasenha = request.form.get('NovaSenha')
    novasenhaconfirm = request.form.get('senhaConfi')
    if novasenha == novasenhaconfirm :
        atualizarSenha(nome,novasenha)
        flash('Senha trocado com sucesso!')
        return redirect(url_for('front_controller.principal'))
    else:
        flash("Confira sua senha!")
        return redirect(url_for('front_controller.atualizar'))
#---------------- Rota Finalizar sessão ----------------------------#
@front_controller.route('/sair', methods=["GET", "POST"])
def sair( ):
    session.pop('usuarioLogado', None)
    resp = make_response(redirect(url_for('front_controller.principal')))
    resp.set_cookie('usuarioLogado', '',0)
    flash("Você foi deslogado com sucesso.")
    return resp