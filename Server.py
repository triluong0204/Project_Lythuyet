from flask import Flask, render_template, request, jsonify, json
from flask_mqtt import Mqtt
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

from sqlalchemy import true
app = Flask(__name__, template_folder='templates')

app.config['MQTT_BROKER_URL'] = 'mqtt.flespi.io'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_CLIENT_ID'] = 'flask_mqtt'
app.config['MQTT_CLEAN_SESSION'] = True
# change with your Flespi token
app.config['MQTT_USERNAME'] = 'FlespiToken lCG8yJPUWRc9awe3M2AaTuKcqd5N4Nvgd1cByPklwkiuGmogcOgW6QWmURXOujSx'
app.config['MQTT_PASSWORD'] = '6m2sckr'
app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds
# create database in https://www.freemysqlhosting.net/          //cho de tao tai khoan free host
# format Url: mysql://username:password@host/databasename
# default port 3306

#mysql://sql6495784:@sql6.freemysqlhosting.net/sql6495784

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1/sensor'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@127.0.0.1/data'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1/sql6495784'
mqtt = Mqtt(app)
db = SQLAlchemy(app)



#format insert table
#INSERT INTO `Data` (`id`, `temp`, `date`, `hour`) VALUES ('1', '1 1 1 1 1', '2022-05-02', '05:15:17');
#format select 
#


def get_duplicate_list(l):
    seen = []
    return [x for x in l if not seen.append(x) and seen.count(x) == 2]

def insert(value):
    value2 = ["",""]
    value2 = value.split(",")
    listdata = []
    temp_listdata = []
    # sugar, salt, almonds, dry rose petal
    # Gulab Badam Chikki
    for i in range(len(value2)):
        val = "%, " +  value2[i] + ",%"
        rows = db.engine.execute('SELECT Name_food FROM mytable WHERE (description_food LIKE %s)', val)
        sql1 = "INSERT INTO `monan`(`Name_food`) VALUES (%s)"
        val1 = value2[i]
        db.engine.execute(sql1, val1)
        for k in rows:
            temp_listdata.append(k.Name_food)
        listdata.append(temp_listdata)

    res = list(set(i for j in listdata for i in j))
    result = set.intersection(*map(set,listdata))
    print(result)

    temp_listdata1 = []
    final_result = []
    for data in result:
        rows = db.engine.execute('SELECT description_food FROM mytable WHERE (Name_food = %s)', data)
        for k in rows:
            demo = str(k)
            a = demo.replace("Key Ingredients: ", "")
            a = a.split(",")
            for item in a:
                b = item.strip("'")
                b = b.strip('"')
                temp_listdata1.append(b)
                s = set(temp_listdata1)
                unique_l = list(s)
            result =  all(elem in unique_l for elem in value2)
            if (result == true):
                # if (len(value2) >= len(unique_l) - 5):
                #     final_result.append(data)
                final_result.append(data)
    
    for data in res:
        sql = "INSERT INTO `result`(`Name_food`) VALUES (%s)"
        val = (data)
        db.engine.execute(sql, val)
    db.session.commit()


@app.route('/')
def index():
    return render_template('./index.html')

@app.route('/data', methods=['GET'])
def data():
    rows = db.engine.execute('SELECT Name_food FROM result ORDER BY ID_result DESC LIMIT 10')
    listdata = []
    for i in rows:
        dictdata = {
            "temp" : i.Name_food
        }
        listdata.append(dictdata)
    return json.dumps(listdata)

@app.route('/hud', methods=['GET'])
def data2():
    rows = db.engine.execute('SELECT Name_food FROM monan ORDER BY ID_food DESC LIMIT 10')
    listdata = []
    for i in rows:
        dictdata = {
            "temp" : i.Name_food
        }
        listdata.append(dictdata)
    return json.dumps(listdata)

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('crawldata')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    if data["topic"] == "crawldata":
        insert(data["payload"])
        
if __name__ == '__main__':
    db.engine.execute('SET SQL_SAFE_UPDATES = 0')
    db.engine.execute('DELETE FROM result;')
    db.engine.execute('DELETE FROM Monan;')
    db.engine.execute('ALTER TABLE result AUTO_INCREMENT = 1')
    db.engine.execute('ALTER TABLE Monan AUTO_INCREMENT = 1')
    app.run()



#SELECT * FROM mytable WHERE Describe_food LIKE "Apple,%"; //data dung o dau
#SELECT * FROM mytable WHERE Describe_food LIKE "%, Cinnamon Powder"; //data dung o cuoi
#SELECT * FROM mytable WHERE Describe_food LIKE "%, Baking Powder,%"; // dung o giua
#SELECT * FROM mytable WHERE (Describe_food LIKE "%, Baking Powder,%") AND (Describe_food LIKE "%, Cinnamon Powder"); //ket hop

#  SELECT *
#  FROM (SELECT * FROM mytable WHERE (Describe_food LIKE "%, Baking Powder,%")) AS temp1
#  INNER JOIN (SELECT * FROM mytable WHERE (Describe_food LIKE "%, Cinnamon Powder")) AS temp2 ON temp1.Food_ID = temp2.Food_ID
#  INNER JOIN (SELECT * FROM mytable WHERE (Describe_food LIKE "Apple,%")) AS temp3 ON temp3.Food_ID = temp2.Food_ID
#SELECT * FROM (SELECT * FROM mytable WHERE (Describe_food LIKE "%, Baking Powder,%")) AS temp1 INNER JOIN (SELECT * FROM mytable WHERE (Describe_food LIKE "%, Cinnamon Powder")) AS temp2 ON temp1.Food_ID = temp2.Food_ID INNER JOIN (SELECT * FROM mytable WHERE (Describe_food LIKE "Apple,%")) AS temp3 ON temp3.Food_ID = temp2.Food_ID


# đầu + giữa
# SELECT * FROM 
# (SELECT * FROM mytable WHERE (Describe_food LIKE "%, Baking Powder,%")) as T1 LEFT JOIN (SELECT * FROM mytable WHERE (Describe_food LIKE "%, Cinnamon Powder")) AS T2 ON T1.Food_ID = T2.Food_ID
# UNION
# SELECT * FROM 
# (SELECT * FROM mytable WHERE (Describe_food LIKE "%, Baking Powder,%")) as T1 RIGHT JOIN (SELECT * FROM mytable WHERE (Describe_food LIKE "%, Cinnamon Powder")) AS T2 ON T1.Food_ID = T2.Food_ID
#SELECT * FROM (SELECT * FROM mytable WHERE (Describe_food LIKE "%, Baking Powder,%")) as T1 LEFT JOIN (SELECT * FROM mytable WHERE (Describe_food LIKE "%, Cinnamon Powder")) AS T2 ON T1.Food_ID = T2.Food_ID UNION SELECT * FROM (SELECT * FROM mytable WHERE (Describe_food LIKE "%, Baking Powder,%")) as T1 RIGHT JOIN (SELECT * FROM mytable WHERE (Describe_food LIKE "%, Cinnamon Powder")) AS T2 ON T1.Food_ID = T2.Food_ID