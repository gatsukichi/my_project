import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.dbmyproject

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('http://fow.kr/champs', headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

db.champion_info.delete_many({})
champions = soup.select(
    'body > div:nth-child(4) > div:nth-child(2) > div > div:nth-child(5) > div:nth-child(5) > ul > a')
e_champions = soup.select('body > div:nth-child(4) > div:nth-child(2) > div > div:nth-child(5) > div:nth-child(5) > ul')

#champion_ename = champion.select_one('a')['href'].text
#
# body > div:nth-child(4) > div:nth-child(2) > div > div:nth-child(5) > div:nth-child(5) > ul > a:nth-child(1)
champion_info = []
for champion in champions:

    champion_rname = champion.select_one('li.champ_one')["rname"]
    champion_cname = champion.select_one('li.champ_one')["cname"]
    champion_img = champion.select_one('li.champ_one > img')["src"]
    champion_ename = champion["href"].split("/")[2]
    champion_info.append({"rname": champion_rname, "cname": champion_cname,"ename":champion_ename, "img": champion_img})

db.champion_info.insert_many(champion_info)
