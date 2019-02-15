from flask import Blueprint
from flask import render_template

statistics_blueprint = Blueprint(
    "statistics_blueprint", __name__, url_prefix="/statistics"
)


@statistics_blueprint.route("/")
def statistics():
    return render_template("statistics.html")
