import os
import markdown
from modules import constants
import flask


def load_base():
    base_path = os.path.join(flask.current_app.root_path,
                             flask.current_app.template_folder,
                             constants.DOCS_BASE_TEMPLATE)
    with open(base_path) as base:
        return base.read()


def markdown_to_html(base, file_to_convert, path):
    with open(os.path.join(constants.ROOT_DIR, file_to_convert), 'r') as md_file:
        all_file = md_file.read()
    html = markdown.markdown(all_file)
    with open(os.path.join(constants.ROOT_DIR, path), 'w') as html_file:
        html_file.write(base.replace('%DOCUMENTATION%', html))


def convert_all_md(dir_to_convert, path):
    base = load_base()
    for file_to_convert in os.listdir(dir_to_convert):
        filename, ext = os.path.splitext(file_to_convert)
        if ext == '.md':
            markdown_to_html(base,
                             os.path.join(dir_to_convert, file_to_convert),
                             os.path.join(path, filename + '.jinja2'))
