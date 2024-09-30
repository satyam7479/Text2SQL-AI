from vanna.flask import VannaFlaskApp
from app.AImodel import vanna  
if __name__ == "__main__":
    app = VannaFlaskApp(vn=vanna.vn)
    app.flask_app.run(host="192.168.1.114", port=5000, debug=True)
    print("http://192.168.1.114:5000/")