from flask import Flask, render_template, request, jsonify, url_for
import google.generativeai as genai
import os
from dotenv import load_dotenv
from markupsafe import escape
import markdown
import PIL.Image
import mimetypes

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads/"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
load_dotenv()


genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")

ALLOWED_MIME_TYPES = {
    "application/pdf", "application/x-javascript", "text/javascript",
    "application/x-python", "text/x-python", "text/plain", "text/html",
    "text/css", "text/md", "text/csv", "text/xml", "text/rtf",
    "image/jpeg", "image/png", "image/gif"
}

def allowed_file(filename):
    # Check if the file has one of the allowed extensions
    mime_type = mimetypes.guess_type(filename)[0]
    return mime_type in ALLOWED_MIME_TYPES


@app.route("/", methods=["GET","POST"])
def index():
    gemini_response = ""
    uploaded_file_url = ""
    if request.method == "POST":
        prompt = request.form.get("prompt", "")
        file = request.files.get("file")
        if file:
            if allowed_file(file.filename):
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                file.save(file_path)
                if file.mimetype.startswith("image"):
                    organ = PIL.Image.open(file)
                    response = model.generate_content([prompt, organ])
                else:
                    file_to_upload = genai.upload_file(file_path)
                    response = model.generate_content([prompt, file_to_upload])
                gemini_response = response.text
                gemini_response = markdown.markdown(gemini_response)
            else:
                gemini_response = "File type not allowed. Please upload a file of type: " + ", ".join(ALLOWED_MIME_TYPES)
        else:
            gemini_response = model.generate_content(prompt)
            gemini_response = markdown.markdown(gemini_response)

    return render_template("index.html", gemini_response=gemini_response, uploaded_file_url=uploaded_file_url)