from flask import current_app as app
from flask import render_template
import hc_scoring.api.files as pf

@app.route("/")
def home():
    return render_template(
        "index.jinja2",
        title="Credit scoring",
        description="Model from Home Credit data",
        template="home-template",
        body="This is a homepage served with Flask.",
    )

@app.route('/api/v1/resources/applications/random', methods=['GET'])
def api_random_application():
    return pf.get_test_application(app.config.get("DATA_PATH")).to_json()