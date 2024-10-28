from flask import current_app as app
from flask import request
from main import extractImage
from main import tools
import json
from jose import jwt

class ExtractImage:
    
    def upload_image(self):
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

    # API endpoint to upload image directly via POST request
    def extract_data_api(self):
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
                access_token = request.headers.get('AccessToken')

                token_data = jwt.decode(access_token, app.config['SECRET_KEY'])
                user = app.db.users.find_one({ "id": token_data['user_id'] }, {
                    "_id": 0,
                    "password": 0
                })

                extractImage.store_image_data_db(extracted_data, user)
            except Exception as e:
                return tools.JsonResp({ "message": "Failed to extract data" }, 500)

            return tools.JsonResp(json.loads(extracted_data), 200)
        else:
            return tools.JsonResp({ "message": "Failed to optimize the image." }, 500)