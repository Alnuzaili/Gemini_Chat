from flask import Flask, render_template, request, jsonify, url_for
import google.generativeai as genai
import os
from dotenv import load_dotenv
from markupsafe import escape
import markdown

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads/"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
load_dotenv()


genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")
# response = model.generate_content("Write a story about a magic backpack.")
# print(response)


@app.route("/", methods=["GET","POST"])
def index():
    gemini_response = ""
    uploaded_image_url = ""
    if request.method == "POST":
        prompt = request.form.get("prompt", "")
        image = request.files.get("file")

        # Mock Gemini response for example purposes
        response = model.generate_content(prompt)
        gemini_response = response.text
        gemini_response = markdown.markdown(gemini_response)
        
        if image:
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
            image.save(image_path)
            uploaded_image_url = url_for("static", filename=f"uploads/{image.filename}")

    return render_template("index.html", gemini_response=gemini_response, uploaded_image_url=uploaded_image_url)