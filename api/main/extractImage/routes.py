from flask import Blueprint
from flask import current_app as app
from main.auth import token_required
from main.extractImage.models import ExtractImage

extract_blueprint = Blueprint("extract", __name__)


@extract_blueprint.route("/optimize", methods=["POST"])
@token_required
def upload_image():
	return ExtractImage().upload_image()

@extract_blueprint.route("/", methods=["POST"])
@token_required
def extract_data_api():
	return ExtractImage().extract_data_api()

@extract_blueprint.route("/get_patient_data/<patient_id>", methods=["GET"])
@token_required
def get_patient_data(patient_id):
	return ExtractImage().get_patient_data(patient_id)