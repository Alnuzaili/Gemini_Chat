from flask import Flask, render_template, request, jsonify, url_for
import google.generativeai as genai
from google.generativeai import caching
import os
from dotenv import load_dotenv
from markupsafe import escape
import markdown
import mimetypes
import datetime
import time

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads/"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
load_dotenv()


ALLOWED_MIME_TYPES = {
    "application/pdf", "application/x-javascript", "application/x-python",
    "text/javascript", "text/x-python", "text/plain", "text/html",
    "text/css", "text/md", "text/csv", "text/xml", "text/rtf",
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/heic", "image/heif",
    "video/mp4","video/mpeg","video/mov","video/avi","video/x-flv","video/mpg","video/webm","video/wmv","video/3gpp",
    "audio/wav", "audio/mp3", "audio/aiff", "audio/aac", "audio/ogg", "audio/flac"
}

def allowed_file(filename):
    # Check if the file has one of the allowed extensions
    mime_type = mimetypes.guess_type(filename)[0]
    return mime_type in ALLOWED_MIME_TYPES


@app.route("/", methods=["GET","POST"])
def index():
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")

    gemini_response = ""
    uploaded_file_url = ""
    if request.method == "POST":
        prompt = request.form.get("prompt", "")
        file = request.files.get("file")
        if file:
            if allowed_file(file.filename):
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                file.save(file_path)
                file_to_upload = genai.upload_file(file_path)
                response = model.generate_content([prompt, file_to_upload])
                gemini_response = response.text
                gemini_response = markdown.markdown(gemini_response)
            else:
                gemini_response = "File type not allowed. Please upload a file of type: " + ", ".join(ALLOWED_MIME_TYPES)
        else:
            response = model.generate_content(prompt)
            gemini_response = response.text
            gemini_response = markdown.markdown(gemini_response)

    return render_template("index.html", gemini_response=gemini_response, uploaded_file_url=uploaded_file_url)








#####################
## Context Caching ##
#####################

# @app.route("/context-caching", methods=["GET","POST"])
# def context_caching():
#     genai.configure(api_key=os.environ["GEMINI_CONTEXT_CASHING_API_KEY"])
#     path_to_video_file = 'Sherlock_Jr_FullMovie.mp4'

#     # Upload the video using the Files API
#     video_file = genai.upload_file(path=path_to_video_file)

#     # Wait for the file to finish processing
#     while video_file.state.name == 'PROCESSING':
#         print('Waiting for video to be processed.')
#         time.sleep(2)
#         video_file = genai.get_file(video_file.name)

#     print(f'Video processing complete: {video_file.uri}')

#     # Create a cache with a 5 minute TTL
#     cache = caching.CachedContent.create(
#         model='models/gemini-1.5-flash-001',
#         display_name='sherlock jr movie', # used to identify the cache
#         system_instruction=(
#             'You are an expert video analyzer, and your job is to answer '
#             'the user\'s query based on the video file you have access to.'
#         ),
#         contents=[video_file],
#         ttl=datetime.timedelta(minutes=5),
#     )

#     # Construct a GenerativeModel which uses the created cache.
#     model = genai.GenerativeModel.from_cached_content(cached_content=cache)


#     gemini_response = ""
#     uploaded_file_url = ""
#     if request.method == "POST":
#         prompt = request.form.get("prompt", "")
#         file = request.files.get("file")
#         if file:
#             if allowed_file(file.filename):
#                 file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
#                 file.save(file_path)
#                 file_to_upload = genai.upload_file(file_path)
#                 response = model.generate_content([prompt, file_to_upload])
#                 gemini_response = response.text
#                 gemini_response = markdown.markdown(gemini_response)
#             else:
#                 gemini_response = "File type not allowed. Please upload a file of type: " + ", ".join(ALLOWED_MIME_TYPES)
#         else:
#             gemini_response = model.generate_content(prompt)
#             gemini_response = markdown.markdown(gemini_response)

#     return render_template("context-caching.html", gemini_response=gemini_response, uploaded_file_url=uploaded_file_url)



#################
### Grounding ###
#################
@app.route("/grounding", methods=["GET","POST"])
def grounding():
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')

    gemini_response = ""
    if request.method == "POST":
        prompt = request.form.get("prompt", "")       
        response = model.generate_content(contents=prompt, tools='google_search_retrieval')
        gemini_response = response.text
        gemini_response = markdown.markdown(gemini_response)

    return render_template("grounding.html", gemini_response=gemini_response)

########################
### Code - Execution ###
########################
@app.route("/code-execution", methods=["GET","POST"])
def code_execution():
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(
            model_name='gemini-1.5-pro',
            tools='code_execution')

    gemini_response = ""
    if request.method == "POST":
        prompt = request.form.get("prompt", "")       
        
        response = model.generate_content((
            'What is the sum of the first 50 prime numbers? '
            'Generate and run code for the calculation, and make sure you get all 50.'))

        gemini_response = response.text
        gemini_response = markdown.markdown(gemini_response)

    return render_template("code-execution.html", gemini_response=gemini_response)
