#from ddtrace import patch_all
import json
from flask import Flask
from flask_assets import Environment

#patch_all()


def init_app():
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object("config.Config")
    app.config.from_json("../conf.json")
    assets = Environment()
    assets.init_app(app)

    with app.app_context():
        # Import parts of our core Flask app
        from . import routes
        from .assets import compile_static_assets

        # Import Dash application
        from .plotlydash.dashboard import init_dashboard

        app = init_dashboard(app)

        # Compile static assets
        compile_static_assets(assets)

        return app
