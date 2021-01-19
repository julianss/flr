import requests

class FlareClient():
    def __init__(self, host="http://localhost:6800"):
        self.host = host
        self.headers = {}

    def login(self, login, password, email=False):
        resp = requests.post(self.host + "/auth", json={
            ('login' if not email else 'email'): login,
            'password': password,
        }).json()
        if "result" in resp:
            print("Login succesful")
            self.headers = {'Authorization': 'Bearer ' + resp["result"]}
        else:
            print(resp)

    def call(self, model, method, *args, **kwargs):
        resp = requests.post(self.host + "/call", headers=self.headers, json={
            'model': model,
            'method': method,
            'args': args,
            'kwargs': kwargs
        })
        resp = resp.json()
        if "result" in resp:
            return resp["result"]
        else:
            raise Exception(resp["error"]["message"])
