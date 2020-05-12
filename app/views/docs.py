from flask import Blueprint, render_template
from modules.constants import ROOT_DIR
import os


blueprint = Blueprint(
    'docs', __name__,
    template_folder=os.path.join(ROOT_DIR, 'app/docs/cached'),
    url_prefix='/docs/v1/'
)


@blueprint.route('api_docs')
def api_docs():
    return render_template('api_docs.jinja2')
