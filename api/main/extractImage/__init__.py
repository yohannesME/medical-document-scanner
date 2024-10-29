from flask import current_app as app
import base64
from PIL import Image
import openai
import json
from bson.objectid import ObjectId


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

    Extract the information from the image and structure it into a JSON format as follows:

    PatientDemographics:

    MedicalRecordNumber: Unique identifier for the patient’s medical record.
    DateOfRegistration: Date the patient registered (YYYY-MM-DD format).
    Name: Full name of the patient.
    FatherName: Name of the patient's father.
    GrandFatherName: Name of the patient's grandfather.
    Gender: Patient’s gender (Male/Female).
    Age: Patient’s age.
    Address:
    Region: The region where the patient resides.
    Wereda: Sub-city or district of residence.
    HouseNumber: House number.
    Kebele: Local administrative unit or kebele.
    PhoneNumber: Patient’s contact number.
    HistorySheet (an array with multiple entries if available):

    Date: Date of each medical record entry (YYYY-MM-DD format).
    NameOfPatient: Full name of the patient.
    Age: Patient’s age.
    Sex: Patient’s gender (Male/Female).
    MedicalRecordNumber: The patient's unique medical record identifier.
    MedicalHistory: Summary of the patient's medical history on that date.
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


def get_patient_data(patient_id):
    data = app.db.medical_records.find_one({"_id": ObjectId(patient_id)})
    return data
    