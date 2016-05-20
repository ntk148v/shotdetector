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


@app.route("/detect/<filename>/<int:algorithm>/<int:threshold>/<int:method>")
def detect(filename, algorithm, threshold, method):
    detector = ShotBoundaryDetector(config.UPLOAD_DIR + filename)
    list_index, diff_queue = detector.detect(algorithm, threshold, method)
    list_images = []
    for index in list_index:
        list_images.append(
            url_for('static', filename='images/keyframe_{}.jpg'
                    . format(index)))
    list_diff = []
    i = 1
    for value in diff_queue:
        list_diff.append([i, value['value']])
        i = i + 1
    return render_template('detect.html', list_images=list_images, list_diff=list_diff)


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
                                    filename=filename,
                                    algorithm=request.form['algorithm'],
                                    threshold=request.form['threshold'],
                                    method=request.form['method']))
    return render_template('upload.html')

if __name__ == '__main__':
    app.debug = True
    app.run(debug=True)
