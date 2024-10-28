from flask import current_app as app
import base64
from PIL import Image
import openai
import json


# Function to optimize the image before processing
def optimize_image(image_path):
    optimized_path = "optimized_image.jpg"
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            img.save(optimized_path, optimize=True, quality=85)
        return optimized_path
    except FileNotFoundError:
        print("Image file not found.")
        return None

# Function to encode image to base64
def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        print("Image file not found.")
        return None

def store_image_data_db(extracted_data, user):
    # the database is going to be a a medical record the mongo database
    # cast the exttracted data to a dict
    extracted_data = json.loads(extracted_data)
    extracted_data["user_id"] = user["id"]
    if "organization" in user:
        extracted_data["organization"] = user["organization"]

    app.db.medical_records.insert_one(extracted_data)
    return extracted_data

# Function to extract medical record data using OpenAI API
def extract_medical_record_data(base64_image):

    OPENAI_API_KEY = app.config["OPENAI_API_KEY"]

    # Initialize OpenAI client
    if OPENAI_API_KEY is None:
        raise ValueError("OPENAI_API_KEY is not set. Please set the environment variable.")
    openai.api_key = OPENAI_API_KEY

    system_prompt = f"""
    You are an OCR-like data extraction tool that extracts medical record data from images.

    1. Please extract the data in this medical record, grouping data according to theme/subgroups, and then output into JSON.

    2. Please keep the keys and values of the JSON in the original language.

    3. The type of data you might encounter in the medical record includes but is not limited to: patient information, medical history, diagnoses, medications, lab results, vital signs, treatment plans, and doctor's notes.

    4. If the page contains no relevant data, please output an empty JSON object and don't make up any data.

    5. If there are blank data fields in the medical record, please include them as "null" values in the JSON object.

    6. If there are tables in the medical record, capture all of the rows and columns in the JSON object.
       Even if a column is blank, include it as a key in the JSON object with a null value.

    7. If a row is blank, denote missing fields with "null" values.

    8. Don't interpolate or make up data.

    9. Please maintain the table structure of any data tables, i.e., capture all of the rows and columns in the JSON object.

    10. Ensure that all extracted data complies with privacy regulations and handle any personal identifiable information (PII) appropriately.

    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        response_format={ "type": "json_object" },
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract the data in this medical record and output into JSON"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"}}
                ]
            }
        ],
        temperature=0.0,
        max_tokens=500,
    )


    extracted_data = response.choices[0].message.content
    return extracted_data

