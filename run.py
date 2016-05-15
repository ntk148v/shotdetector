from app.shot_detector import ShotBoundaryDetector
import config

import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug import secure_filename


app = Flask(__name__)
app.config['UPLOAD_DIR'] = config.UPLOAD_DIR


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in config.ALLOWED_EXTENSIONS


@app.route("/detect", methods=['POST'])
def detect():
    detector = ShotBoundaryDetector(request.form['url'])
    detector.detect()
    return "Done!!"


@app.route("/upload", method=['GET', 'POST'])
def upload():
    if(request.method == "POST"):
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return "Done!"


@app.route("/")
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.debug = True
    app.run(debug=True)
