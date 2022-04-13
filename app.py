import requests
from bs4 import BeautifulSoup as bs
from flask import Flask, render_template, request
from flask_cors import cross_origin
import json

import certifi
import pymongo

import logging as lg
lg.basicConfig(filename='ineuron_scrapper_log.log', level=lg.INFO, format="%(asctime)s  %(levelname)s  %(message)s")

app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")


def getcourses():
    try:
        url = "https://courses.ineuron.ai/"
        r = requests.get(url)
        htmlcontent = r.content
        soup = bs(htmlcontent, 'html.parser')
        script = str(soup.findAll('script', {"id": "__NEXT_DATA__", "type": "application/json"}))
        final = script[52:-10]
        dict = json.loads(final)
        cat = dict['props']['pageProps']['initialState']['init']['categories']
        courses = {}
        for i in cat.keys():
            sub = []
            c = cat[i]['title']
            for j in cat[i]['subCategories'].keys():
                sub.append(cat[i]['subCategories'][j]['title'])
            courses[c] = sub
        lg.info("Courses scrapped : ",courses)
        return courses
    except Exception as e:
        lg.error("Scapper failed : ",str(e))
        return 'SOMETHING IS WRONG '+str(e)

@app.route('/displaycourses',methods=['GET','POST']) #route to display result page
@cross_origin()
def displaycourses():
    try:
        result={}
        dict=getcourses()
        for i in dict.keys():
            s=str(dict[i])
            s=s[1:len(s)-1]
            result[i]=s
        lg.info("Courses Displayed ")
        return render_template('results.html', courses=result)
    except Exception as e:
        lg.error('Cannot display courses : ', str(e))
        return 'SOMETHING IS WRONG'


@app.route('/dboperation',methods=['GET','POST']) #route to display db form
@cross_origin()
def dbpage():
    return render_template('dboperation.html')


@app.route('/dbinsert',methods=['GET','POST']) #route to perform db insertion
@cross_origin()
def mongoinsert():
    if request.method=='POST':
        try:
            data = getcourses()
            pw = request.form['password']
            db_name = request.form['db_name']
            col_name = request.form['collection']
            url='mongodb+srv://mongodb:' + pw + '@cluster0.ktmti.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
            client = pymongo.MongoClient(url,tlsCAFile=certifi.where())
            lg.info("Pymongo client created ")
        except Exception as e:
            print("Error while creating pymongo client, check logs")
            lg.error('Cannot create pymongo client : ',str(e))
            return render_template('dbresult.html', msg="SOMETHING IS WRONG")
        try:
            db = client[db_name]
            col = db[col_name]
            col.insert_one(data)
            lg.info('Data added into pymongo collection : ')
            return render_template('dbresult.html', msg="Data added : Check your database")
        except Exception as e:
            print("ERROR", str(e))
            lg.error('Cannot insert data into mongodb collection : ', str(e))
            return render_template('dbresult.html', msg="SOMETHING IS WRONG")


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8002, debug=True)












