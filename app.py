from flask import Flask, render_template, request, jsonify, url_for
import google.generativeai as genai
import os
from dotenv import load_dotenv
from markupsafe import escape
import markdown
import PIL.Image

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads/"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
load_dotenv()


genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}

def allowed_file(filename):
    # Check if the file has one of the allowed extensions
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET","POST"])
def index():
    gemini_response = ""
    uploaded_image_url = ""
    if request.method == "POST":
        prompt = request.form.get("prompt", "")
        image = request.files.get("file")

        if allowed_file(image.filename):
            # Mock Gemini response for example purposes
            organ = PIL.Image.open(image)
            response = model.generate_content([prompt, organ])
            gemini_response = response.text
            gemini_response = markdown.markdown(gemini_response)
        else:
            gemini_response = "File type not allowed. Please upload an image file."
        if image:
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
            image.save(image_path)
            uploaded_image_url = url_for("static", filename=f"uploads/{image.filename}")

    return render_template("index.html", gemini_response=gemini_response, uploaded_image_url=uploaded_image_url)