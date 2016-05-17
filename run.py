from app.shot_detector import ShotBoundaryDetector
import config
import logging

import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug import secure_filename


app = Flask(__name__)
logger = logging.getLogger(__name__)

app.config['UPLOAD_DIR'] = config.UPLOAD_DIR


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in config.ALLOWED_EXTENSIONS


@app.route("/detect/<filename>/<int:algorithm>/<int:threshold>")
def detect(filename, algorithm, threshold):
    detector = ShotBoundaryDetector(config.UPLOAD_DIR + filename)
    list_index = detector.detect(algorithm, threshold)
    list_images = []
    for index in list_index:
        list_images.append(url_for('static', filename='images/keyframe_{}.jpg'. format(index)))
    return render_template('detect.html', list_images=list_images)


@app.route("/", methods=['GET', 'POST'])
def home():
    if(request.method == "POST"):
        file = request.files['uploadFile']
        if file and allowed_file(file.filename):
            logger.info("{}" . format(file.filename))
            filename = secure_filename(file.filename)
            if not (os.path.exists(app.config['UPLOAD_DIR']) or
                    os.path.isdir(app.config['UPLOAD_DIR'])):
                os.makedirs(app.config['UPLOAD_DIR'])
            file.save(os.path.join(app.config['UPLOAD_DIR'], filename))
            return redirect(url_for('detect',
                                    filename=filename, algorithm=request.form['algorithm'], threshold=request.form['threshold']))
    return render_template('upload.html')

if __name__ == '__main__':
    app.debug = True
    app.run(debug=True)
