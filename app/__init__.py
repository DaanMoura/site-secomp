from os import path, getenv

from flask import Flask, redirect, request, render_template, session
from flask_babelex import Babel
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate


def create_app(config=None):
    """
    Project app factory
    """

    configs = {
        'development': '.development',
        'production': '.production',
        'default': '.default'
    }

    if config not in configs:
        config = getenv("FLASK_CONFIGURATION", "default")

    config = 'app.config' + configs[config]

    app = Flask(__name__)
    app.config.from_object(config)

    Bootstrap(app)

    @app.errorhandler(400)
    def bad_request(error):
        return render_template('400.html'), 400

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('500.html'), 500

    from app.models.models import db, Usuario
    from app.models.commands import populate

    app.app_context().push()
    db.init_app(app)
    migrate = Migrate(app, db)

    @app.cli.command()
    def create():
        """
        Creates database tables from sqlalchemy models
        """
        db.create_all()
        populate()

    @app.cli.command()
    def drop():
        """
        Drops database tables
        """
        prompt = input('Erase current database? [y/n]')
        if prompt == 'y':
            db.session.close_all()
            db.drop_all()

    from app.controllers.functions.email import mail

    mail.init_app(app)

    from app.controllers.routes import admin, management, users, views

    app.register_blueprint(management.management)
    app.register_blueprint(users.users)
    app.register_blueprint(views.views)

    upload_path = path.join(path.dirname(__file__), 'static')
    adm = admin.init_app(app, upload_path)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def user_loader(user_id):
        return db.session.query(Usuario).filter_by(id=user_id).first()

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return redirect('/login')

    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        if request.args.get('lang'):
            session['lang'] = request.args.get('lang')
        return "pt"

    return app

