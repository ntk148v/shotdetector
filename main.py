from shot_detector import ShotBoundaryDetector
from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/start", methods=['POST'])
def start():
    detector = ShotBoundaryDetector(request.form['url'])
    detector.detect()
    return "Done!!"

@app.route("/")
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.debug = True
    app.run(debug = True)

# if __name__ == '__main__':
#     detector = ShotBoundaryDetector('test.avi')
#     detector.detect()
