#!/usr/bin/python3
from client import FlareClient
client = FlareClient()
client.login("admin","admin")
res = client.call("Person","read",
    fields=["name","age","favorite_color"],
    filters=[('name','=','John')])
assert len(res) == 1
assert res[0]["name"] == "John"
assert res[0]["age"] == 25
assert res[0]["favorite_color"] == "G"