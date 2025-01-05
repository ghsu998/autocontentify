from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "AutoContentify is running!"

if __name__ == "__main__":
    # 運行在 80 端口
    app.run(host="0.0.0.0", port=80)

