from flask import Flask
import os

file_path = os.path.abspath(os.getcwd())

app = Flask(__name__)

@app.route("/")
def hello():
    s = "Hello!<BR>"
    s += "getcwd: "+os.getcwd()+"<BR>"
    s += "file_path:"+file_path+"<BR>"

    return s

if __name__ == "__main__":
    app.run()

