from flask import render_template, request, Blueprint, url_for, redirect
from flask_login import login_required, login_user, logout_user, current_user
from passlib.hash import pbkdf2_sha256

from app.controllers.forms.forms import *
from app.controllers.functions.email import enviar_email_dm
from app.controllers.constants import *

views = Blueprint('views', __name__, static_folder='static', template_folder='templates')


@views.route('/', methods=["GET", "POST"])
def index():
    """
    Renderiza a página inicial do projeto
    """
    form_login = LoginForm(request.form)
    return render_template('views/index.html', title='Página inicial',
                           secomp_now=secomp_now[0], secomp=secomp[0],
                           secomp_email=secomp_email,
                           secompEdition=secomp_edition,
                           form_login=form_login)


@views.route('/contato', methods=['POST', 'GET'])
def contato_dm():
    """
    Página de contato
    """
    form = ContatoForm(request.form)
    form_login = LoginForm(request.form)
    if form.validate_on_submit():
        nome = form.nome_completo.data
        email = form.email.data
        mensagem = form.mensagem.data
        enviar_email_dm(nome, email, mensagem)
        return render_template('views/contato.html', form=form, enviado=True, form_login=form_login)
    return render_template('views/contato.html', form=form, form_login=form_login)


@views.route('/constr', methods=["GET", "POST"])
def constr():
    form_login = LoginForm(request.form)
    return render_template('views/em_constr.html', title='Página em construção', form_login=form_login)


@views.route('/sobre', methods=["GET", "POST"])
def sobre():
    form_login = LoginForm(request.form)
    return render_template('views/sobre.html', title='Sobre a Secomp', form_login=form_login)


@views.route('/cronograma', methods=["GET", "POST"])
def cronograma():
    form_login = LoginForm(request.form)
    return render_template('views/cronograma.html', title='Cronograma', form_login=form_login)


@views.route('/equipe', methods=["GET", "POST"])
def equipe():
    import json
    import os.path as op
    import app.config as conf
    form_login = LoginForm(request.form)
    filename = op.join(op.dirname(conf.__file__), 'membros_org.json')
    with open(filename, 'r') as read_file:
        data = json.load(read_file)
    return render_template('views/equipe.html', title='Equipe', data=data, form_login=form_login)


@views.route('/faq', methods=["GET", "POST"])
def faq():
    form_login = LoginForm(request.form)
    return render_template('views/faq.html', title='FAQ', form_login=form_login)

@views.route('/teste', methods=["GET","POST"])
def teste():
    form_login = LoginForm(request.form)
    return render_template('teste.html', title='Teste', form_login=form_login)

@views.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        user = db.session.query(Usuario).filter_by(
            email=form.email.data).first()
        if user:
            if pbkdf2_sha256.verify(form.senha.data, user.senha):
                user.autenticado = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for('users.dashboard'))
        return render_template('views/login.html', form_login=form, form=form, erro=True)
    return render_template('views/login.html', form_login=form, form=form)


@views.route("/logout", methods=["GET"])
@login_required
def logout():
    """
    Renderiza a página de logout do projeto
    """
    user = current_user
    user.autenticado = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('.index'))

@views.route("/senhas", methods=["GET"])
def senhas():
    return render_template('views/requisito_50.html')
