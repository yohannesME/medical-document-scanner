from flask import current_app as app
from flask import request
from main import extractImage
from main import tools
import json
from jose import jwt
from bson.objectid import ObjectId

class ExtractImage:
    def get_user_from_token(self):
        # get the user access token
        access_token = request.headers.get('AccessToken')

        token_data = jwt.decode(access_token, app.config['SECRET_KEY'])

        user = app.db.users.find_one({ "id": token_data['user_id'] }, {
            "_id": 0,
            "password": 0
        })

        return user

    def upload_image(self):
        try: 
            if 'image' not in request.files:
                return tools.JsonResp({ "message": "No image file provided" }, 400)

            image = request.files['image']
            image_path = "uploaded_image.jpg"
            image.save(image_path)

            # Step 1: Optimize the image
            optimized_image_path = extractImage.optimize_image(image_path)

            if optimized_image_path:
                # Step 2: Convert optimized image to base64
                base64_image = extractImage.encode_image(optimized_image_path)

                # Step 3: Extract data from the medical record using OpenAI API
                try:
                    extracted_data = extractImage.extract_medical_record_data(base64_image)
                except Exception as e:
                    return tools.JsonResp({ "message": "Failed to extract data" }, 500)


                return tools.JsonResp(json.loads(extracted_data), 200)
            else:
                return tools.JsonResp({ "message": "Failed to optimize the image." }, 500)
        except Exception as e:
            return tools.JsonResp({ "message": "Invalid Request" }, 500)

    # API endpoint to upload image directly via POST request
    def extract_data_api(self):
        try: 
            if 'image' not in request.files:
                return tools.JsonResp({ "message": "No image file provided" }, 400)

            image = request.files['image']
            image_path = "uploaded_image.jpg"
            image.save(image_path)


            # Step 1: Optimize the image
            optimized_image_path = extractImage.optimize_image(image_path)

            if optimized_image_path:
                # Step 2: Convert optimized image to base64
                base64_image = extractImage.encode_image(optimized_image_path)

                # Step 3: Extract data from the medical record using OpenAI API
                # extracted_data = extractImage.extract_medical_record_data(base64_image)
                try:
                    extracted_data = extractImage.extract_medical_record_data(base64_image)
                    user = self.get_user_from_token()
                    medical_record_id = extractImage.store_image_data_db(extracted_data, user)
                    extracted_data = json.loads(extracted_data)
                    extracted_data["_id"] = medical_record_id
                    return tools.JsonResp({ "message": "Successfully extracted data", "data": extracted_data }, 200)
                except Exception as e:
                    return tools.JsonResp({ "message": "Failed to extract data" }, 500)

            else:
                return tools.JsonResp({ "message": "Failed to optimize the image." }, 500)
        except Exception as e:
            return tools.JsonResp({ "message": "Invalid Request" }, 500)
    
    def get_patient_data(self, patient_id):
        try:
            extracted_data = extractImage.get_patient_data(patient_id)

            if extracted_data is None:
                return tools.JsonResp({ "message": "Patient data not found." }, 500)
            return tools.JsonResp(extracted_data, 200)
        except Exception as e:
            return tools.JsonResp({ "message": "Failed to get patient data" }, 500)
    
    # search for patient data by their name, email or phone number 
    def search_patient_data(self):
        try:
            # extract the body from the request
            data = json.loads(request.data)
            search_term = data["query"]
            extracted_data = extractImage.search_patient_data(search_term)
            return tools.JsonResp(extracted_data, 200)
        except:
            return tools.JsonResp({ "message": "Failed to search patient data" }, 500)

    def patient_data(self):
        try:
            # get the user access token
            user = self.get_user_from_token()
            if user.get("is_admin") is False:
                if user.get("organization") is None:
                    return tools.JsonResp({ "message": "No Records" }, 401)
                patient_data = app.db.medical_records.find({"organization" : user["organization"]})
            else:
                # get all the patient data from the database
                patient_data = app.db.medical_records.find()
            patient_data = list(patient_data)

            return tools.JsonResp({"data" : patient_data, "count": len(patient_data)}, 200)
        except:
            return tools.JsonResp({"message": "Failed to load the data"},500)
    
    def delete_patient_data(self, id):
        try:
            # delete the patient data from the database
            app.db.medical_records.delete_one({"_id": ObjectId(id)})
            return tools.JsonResp({ "message": "Patient data deleted" }, 200)
        except:
            return tools.JsonResp({ "message": "Failed to delete patient data" }, 500)
    