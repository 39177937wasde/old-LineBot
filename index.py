
from re import I
import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("D://資訊管理導論/mis-s1091785/misiia-firebase-adminsdk-nsa58-f993d289ac.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
from flask import Flask, render_template, request,url_for,redirect, request, abort
from datetime import datetime, timezone, timedelta
from waitress import serve

import requests
from bs4 import BeautifulSoup

from apscheduler.schedulers.blocking import BlockingScheduler
sched = BlockingScheduler()
from linebot import LineBotApi
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import ( MessageEvent, TextMessage, TextSendMessage,ImageSendMessage, LocationSendMessage)
line_bot_api = LineBotApi("5SwJl5rBRAT5k2v5FYVZzKacg8+tdZ/oJHu0/qHS51sKIsIQ2cjpmXSxSQ2knWVcm3iiJRMn22QZRyKHhqSlhUwpo1GrT8EqZN9dHWgSP/3o/vtLcyCrhg1CM4fVw8s6ubfuptzyZTNpR2D8azk7zwdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("4f5d14dddd6b385a38134722145f7c4c")


app = Flask(__name__)
@sched.scheduled_job("interval", minutes=1)
@app.route("/")
def index():
    homepage = "<h1>陳柏睿Python測試網頁</h1>"
    homepage += "<a href=/mis>MIS</a><br>"
    homepage += "<a href=/current>開啟網頁及顯示日期時間</a><br>"
    homepage += "<a href=/welcome?nick=s1091785>開啟網頁及傳送使用者暱稱</a><br>"
    homepage += "<a href=/hi>計算總拜訪次數</a><br>"
    homepage += "<a href=/read>讀取Firestore資料</a><br>"
    homepage += "<a href=/spider>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    homepage += "<a href=/search>找影片</a><br>"

    return homepage

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1>"

@app.route("/current")
def current():
    tz = timezone(timedelta(hours=+8))
    now = datetime.now(tz)
    return render_template("current.html", datetime = str(now))

@app.route("/welcome", methods=["GET", "POST"])
def welcome():
    user = request.values.get("nick")
    return render_template("welcome.html", name=user)

@app.route("/hi")
def hi():
    # 載入原始檔案
    f = open("D:/visual studio/資訊管理導論/mis-s1091785/count.txt", "r")
    count = int(f.read())
    f.close()

   
    count += 1

    
    f = open("count.txt", "w")
    f.write(str(count))
    f.close()
    return "本網站總拜訪人次：" + str(count)
@app.route("/read")
def read():
    Result = ""     
    collection_ref = db.collection("靜宜資管")    
    docs = collection_ref.order_by("mail", direction=firestore.Query.DESCENDING).get()    
    for doc in docs:         
        Result += "文件內容：{}".format(doc.to_dict()) + "<br>"    
    return Result
@app.route("/spider")
def spider():
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".filmListAllX li")
    lastUpdate = sp.find("div", class_="smaller09").text[5:]
    age=sp.select(".runtime")
    q=[]
    info=""
    for pic in age:
        if(pic.find("img")==None):
            q.append(" ")
            continue
        q.append(pic.find("img").get("src"))
        i=0
    for item in result:
        picture = item.find("img").get("src").replace(" ", "")
        title = item.find("div", class_="filmtitle").text
        movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
        show = item.find("div", class_="runtime").text.replace("上映日期：", "")
        show = show.replace("片長：", "")
        show = show.replace("分", "")
        showDate = show[0:10]
        showLength = show[13:]
        if(q[i]==" "):
            info = "目前此片並沒有分級"+ "\n\n"

        if(q[i]=="/images/cer_G.gif"):

            info = "本片為：普遍級(0歲以上)"+ "\n\n"

        elif(q[i]=="/images/cer_P.gif"):

            info = "本片為：保護級(6歲以上)"+ "\n\n"

        elif(q[i]=="/images/cer_F5.gif"):

            info = "本片為：輔導十五歲級(15歲以上)"+ "\n\n"
        elif(q[i]=="/images/cer_R.gif"):

            info = "本片為：限制十八歲級(18歲以上)"+ "\n\n"


 

        i+=1

        doc = {
            "title": title,
            "age":info,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": showLength,
            "lastUpdate": lastUpdate
         }

        doc_ref = db.collection("電影").document(movie_id)
        doc_ref.set(doc)
    return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 
@app.route("/search", methods=["POST","GET"])
def search():
    if request.method == "POST":
        MovieTitle = request.form["MovieTitle"]
        collection_ref = db.collection("電影")
        docs = collection_ref.order_by("showDate").get()
        info = ""
        j=0
        i=0
        for doc in docs:
            i+=1
        for doc in docs:
            if MovieTitle in doc.to_dict()["title"]: 
                info += "片名：" + doc.to_dict()["title"] + "<br>" 
                info += "海報：" + doc.to_dict()["picture"] + "<br>"
                info +=doc.to_dict()["age"]+"<br>"
                info += "影片介紹：" + doc.to_dict()["hyperlink"] + "<br>"
                if doc.to_dict()["showLength"].isdigit():
                    info += "片長：" + doc.to_dict()["showLength"] + " 分鐘<br>"
                else:
                    info+="目前沒有寫到<br>" 
                info += "上映日期：" + doc.to_dict()["showDate"] + "<br><br>"
            elif j==i-1:
                info+="目前無有關\""+MovieTitle+"\"的電影"
                return info
            else:
                j+=1
        return info
    else:  
        return render_template("input.html")


@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    if(message[:5].upper() == 'MOVIE'):
        res = searchMovie(message[6:])
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = res))
    elif(message.upper() == "MYDOG"):
        line_bot_api.reply_message(event.reply_token, ImageSendMessage(
            original_content_url = "https://www1.pu.edu.tw/~s1091785/mydog.jpg",
            preview_image_url = "https://www1.pu.edu.tw/~s1091785/mydog.jpg"
        ))
    elif(message.upper() == "PU"):
        line_bot_api.reply_message(event.reply_token, LocationSendMessage(
            title = "靜宜大學地理位置",
            address = "台中市沙鹿區臺灣大道七段200號",
            latitude = 24.22649,
            longitude = 120.5780923
        ))

    else:
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text= "我是電影機器人，您輸入的是：" + message + "。祝福您有個美好的一天！" ))
def searchMovie(keyword):
    info = "您要查詢電影，關鍵字為：\n" + keyword
    collection_ref = db.collection("電影")
    docs = collection_ref.order_by("showDate").get()
    found = False
    for doc in docs:
        if keyword in doc.to_dict()["title"]:
            found = True 
            info += "片名：" + doc.to_dict()["title"] + "\n" 
            info += "海報：" + doc.to_dict()["picture"] + "\n"
            info += "影片介紹：" + doc.to_dict()["hyperlink"] + "\n"
            info += "片長：" + doc.to_dict()["showLength"] + " 分鐘\n" 
            info += "上映日期：" + doc.to_dict()["showDate"] + "\n\n"

    if not found:
       info += "很抱歉，目前無符合這個關鍵字的相關電影喔"  
    return info



#if __name__ == "__main__":
    # app.run()
    #serve(app, host='0.0.0.0', port=8080)

app=Flask(__name__)




