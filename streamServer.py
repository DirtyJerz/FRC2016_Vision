#!/usr/bin/env python
from flask import Flask, render_template, Response
from cameras import USBVideoCamera

app = Flask(__name__)

@app.route('/')
def index():
    return """<html>
  <head>
    <title>Video Streaming Demonstration</title>
  </head>
  <body>
    <h1>Video Streaming Demonstration</h1>
    <img id="leftVideo" src="/left_video_feed">
  </body>
</html>"""

def gen(camera, idx):
    while True:
        frame = camera.get_frame(idx)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/left_video_feed')
def left_video_feed():
    return Response(gen(USBVideoCamera(), 0),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
# @app.route('/right_video_feed')
# def right_video_feed():
#     return Response(gen(USBVideoCamera(), 1),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)