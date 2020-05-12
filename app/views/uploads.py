from flask import send_from_directory, Blueprint, current_app


blueprint = Blueprint('upload', __name__)


@blueprint.route('/uploads/<filename>')
def uploaded_file(filename):
    """Возвращает файл из директории UPLOAD_FOLDER."""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
