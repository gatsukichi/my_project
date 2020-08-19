from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbmyproject


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/detail')
def detail():
    name = request.args.get("name")

    return render_template('detail.html')


@app.route('/memo', methods=['POST'])
def post_article():
    print("POST")
    # champion = request.form.get('champion_img')
    # comment_receive = request.form.get('champion_rname')
    # request.form.get('champion_cname')
    # # 1. 클라이언트로부터 데이터를 받기
    #
    # # 2. meta tag를 스크래핑하기
    # db.articles.insert_one(article)
    # # 3. mongoDB에 데이터 넣기
    # return jsonify({'result': 'success', 'msg': 'POST 연결되었습니다!'})


@app.route('/counter', methods=['GET'])
def counter_champion_scraping():
    ename = request.args.get("name")  # 영문 이름 가져올것입니다.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    counter_data = requests.get(f"https://www.op.gg/champion/{ename}/statistics/", headers=headers)
    soup = BeautifulSoup(counter_data.text, 'html.parser')

    counter_champions = soup.select(
        "body > div.l-wrap.l-wrap--champion > div.l-container > div > div.l-champion-statistics-header > div > div.champion-stats-header-matchup > div.tabItems > table.champion-stats-header-matchup__table--strong > tbody > tr ")
    counter_dicted = []
    for counter_champion in counter_champions:
        counters = counter_champion.select_one("td")
        ratio = counter_champion.select_one("td.champion-stats-header-matchup__table__winrate > b ")
        if ratio is not None:
            ratio = ratio.text
        print(counters)

        counter = str.strip(counters.text)
        counter = re.sub("[.'!@#$ ]", '', counter)
        counter = counter.capitalize()
        counter = counter.split("&")[0] # 누누때문에 추가된 코드

        print(counter, ratio)
        counter_on_db = db.champion_info.find_one({"ename": {'$regex': counter, '$options': 'i'}}, {"_id": False})
        counter_on_db["ratio"] = ratio
        print(counter_on_db)
        counter_dicted.append(counter_on_db)

    print(counter_dicted)

    return jsonify({'result': 'success', 'msg': 'GET 연결되었습니다!', "info": counter_dicted})


@app.route('/champion_card_info', methods=['GET'])
def read_champion_data():
    name = request.args.get("name")
    info = list(db.champion_info.find({}, {"_id": False}))
    print(name)

    if name is not None:
        selected_info = db.champion_info.find_one({"ename": name}, {"_id": False})
        print(selected_info)
        return jsonify({'result': 'success', 'msg': 'GET 연결되었습니다!', "info": selected_info})

    return jsonify({'result': 'success', 'msg': 'GET 연결되었습니다!', "info": info})


@app.route('/tier_list', methods=['GET'])
def tier_list_get():
    line = request.args.get("line")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    counter_data = requests.get("https://www.op.gg/champion/statistics", headers=headers)
    soup = BeautifulSoup(counter_data.text, 'html.parser')

    box = soup.select("#body > div.l-wrap.l-wrap--champion > div.l-container")
    print(box)
    # body > div.l - wrap.l - wrap - -champion > div.l - container > div.l - champion - index >
    # div.l - champion - index - content > div.l - champion - index - content - -side >
    # div > div.champion - index - trend - content > div >
    # div.tabItem.champion - trend.champion - trend - tier > div > table
    return jsonify({'result': 'success', 'msg': 'GET 연결되었습니다!'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
