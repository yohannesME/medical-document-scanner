from flask import Blueprint
from flask import current_app as app
from main.auth import token_required
from main.admin import admin_required
from main.admin.models import Admin

admin_blueprint = Blueprint("admin", __name__)

@admin_blueprint.route("/users", methods=["GET"])
@token_required
@admin_required
def get():
	return Admin().listOfUsers()


# activate and deactivate a user
@admin_blueprint.route("/users/activate", methods=["POST"])
@token_required
@admin_required
def activateUser():
	return Admin().activateUser()

@admin_blueprint.route("/users/deactivate", methods=["POST"])
@token_required
@admin_required
def deactivateUser():
	return Admin().deactivateUser()