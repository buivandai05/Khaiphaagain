from flask import Flask
from Config import Config
from routes.main_routes import main_bp

app = Flask(__name__)
app.config.from_object(Config)

# Đăng ký Blueprint các tuyến đường
app.register_blueprint(main_bp)

if __name__ == '__main__':
    print("🚀 Flask Server đang khởi chạy tại: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)