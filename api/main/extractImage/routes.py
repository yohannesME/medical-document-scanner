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


@extract_blueprint.route("/search_patient_data", methods=["GET"])
@token_required
def search_patient_data():
	return ExtractImage().search_patient_data()


@extract_blueprint.route("/patient_data", methods=["GET"])
@token_required
def patient_data():
	return ExtractImage().patient_data()

@extract_blueprint.route("/patient_data/<id>", methods=["DELETE"])
@token_required
def delete_patient_data(id):
	return ExtractImage().delete_patient_data(id)

