import requests
import json
from private import Keys

class app(Keys):

    def __init__(self):
        super().__init__()

    def create(self,email,password):
        url = self.heroku_create_url
        req = requests.post(url,data = {"email":email,"password":password})
        content = json.loads(req.content.decode("utf-8"))
        if(content["email"][0]=="has already been taken"):
            return "er0010"
        else:
            self.getId = content["id"]
            return content

    def login(self,email,password):
        url = self.heroku_login_url
        req = requests.post(url,data={"email":email,"password":password})
        content = json.loads(req.content.decode("utf-8"))
        if "error" in content:
            return "er0110"
        else:
            self.getId = content["id"]
            return content

if __name__ == '__main__':
    cu = app()
    cu.login("vincent1@gmail.com","123456")
    print(cu.getId)

