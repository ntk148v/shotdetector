# from app.shot_detector import ShotBoundaryDetector
import config
import logging

import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename


app = Flask(__name__)
logger = logging.getLogger(__name__)

app.config['UPLOAD_DIR'] = config.UPLOAD_DIR


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in config.ALLOWED_EXTENSIONS


# @app.route("/detect", methods=['POST'])
# def detect():
#     detector = ShotBoundaryDetector(request.form['url'])
#     detector.detect()
#     return "Done!!"

@app.route("/predetect/<filename>")
def predetect(filename):
    return send_from_directory(app.config['UPLOAD_DIR'], filename)


@app.route("/", methods=['GET', 'POST'])
def home():
    if(request.method == "POST"):
        file = request.files['uploadFile']
        if file and allowed_file(file.filename):
            logger.info("{}" . format(file.filename))
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_DIR'], filename))
            return redirect(url_for('predetect',
                                    filename=filename))
    return render_template('upload.html')

if __name__ == '__main__':
    app.debug = True
    app.run(debug=True)
