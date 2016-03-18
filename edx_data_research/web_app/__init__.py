from flask import Flask, render_template

from edx_data_research.web_app.extension import db, mail, security


def create_app(config_object='config'):
    app = Flask(__name__)
    app.config.from_object(config_object)
    register_extensions(app)
    register_flask_security(app)
    register_blueprints(app)
    register_errorhandlers(app)
    return app


def register_extensions(app):
    """Register extensions"""
    db.init_app(app)
    mail.init_app(app)


def register_flask_security(app):
    """Register Flask-Security extension"""
    from flask.ext.security import MongoEngineUserDatastore

    from edx_data_research.web_app.auth.forms import ExtendedRegisterForm
    from edx_data_research.web_app.models import User, Role

    user_datastore = MongoEngineUserDatastore(db, User, Role)
    security = Security(app, user_datastore, register_form=ExtendedRegisterForm)


def register_blueprint(app):
    """Register blueprints"""
    pass


def register_errorhandlers(app):
    """Register error handlers."""
    def render_error(error):
        """Render error template."""
        error_code = getattr(error, 'code', 500)
        return render_template('errors/{0}.html'.format(error_code)), error_code
    for error_code in [404, 500]:
        app.errorhandler(errorcode)(render_error)


@app.route('/')
def index():
    return render_template('index.html')