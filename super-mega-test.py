import requests
print(requests.get('https://geek-jokes.sameerkumar.website/api?format=json').json()["joke"])
print("Hello there!")