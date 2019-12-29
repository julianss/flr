import requests
import names
import random
import datetime
years = range(1950,2005)
def get_random_birthday():
    year = random.choice(years)
    doy = random.randint(1,365)
    fecha = datetime.date(year, 1, 1) + datetime.timedelta(days=doy)
    return fecha.strftime("%Y-%m-%d")

host = "http://localhost:6800"
resp = requests.post(host + "/call", json={
    'model': 'Person',
    'method': 'read',
    'args': [
        ["name"], []
    ],
    'kwargs': {
    }
})
print (resp.text)

# for i in range(0,50):
#     resp = requests.post(host + "/call", json={
#         'model': 'Person',
#         'method': 'create',
#         'args': [
#         ],
#         'kwargs': {
#             "name": names.get_full_name(),
#             "birthday": get_random_birthday(),
#             "salary": round(random.randint(1000,100000), -3)
#         }
#     })
#     print (resp.text)