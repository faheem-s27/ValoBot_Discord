import requests
import urllib.request, json 


r = requests.get('https://api.henrikdev.xyz/valorant/v3/matches/eu/SprinkledRainbow/1593?size=10')

for i in range(0, 10):
    matchID = r.json()["data"][i]["metadata"]["matchid"]
    j = i + 1
    print("Match " +str(j)+ ": https://api.henrikdev.xyz/valorant/v2/match/" + matchID)



def fortniteTest():
    r = requests.get(f"https://fortnite-api.com/v2/stats/br/v2/0eaab3ec71d74f5ebce5d82dce2c0a18", headers={"Authorization": "224e7440-e2c4-4040-88e9-9f4a7214137a"})
    print(r.text)



def FortniteTestName(name):
    r = requests.get(f"https://fortnite-api.com/v2/stats/br/v2?name={name}", headers={"Authorization": "224e7440-e2c4-4040-88e9-9f4a7214137a"})
    print(r.text)


#FortniteTestName("HoneyArif7867")