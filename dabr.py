from flask import Flask
from flask_restful import Api, Resource

from app import DabR

app = Flask(__name__)
api = Api(app)

# from app import routes


class GetIpReputation(Resource):
    def get(self, ip):
        return {"ip": ip, "reputation": DabR.getIpReputation(ip)}


api.add_resource(GetIpReputation, "/getreputation/<string:ip>")


if __name__ == "__main__":
    # print(DabR.getIpReputation("39.40.195.174"))
    app.run(debug=True)
