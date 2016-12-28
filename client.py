#!/usr/bin/python
#-*- coding: utf-8 -*-
from oslo_config import cfg  
import oslo_messaging  
from flask import Flask, redirect, request
import MySQLdb
import json, os
app = Flask(__name__, static_folder='static') 

class Client():
    def __init__(self):
        self.mac = ""
        self.ip = ""

global ip, user, password, database

ip="10.1.101.36"
user = "root"
password = "ccloudhan1"
database = "cvirt"

@app.route('/static/<path:path>')
def static_proxy(path):
    return app.send_static_file(path)

@app.route('/upload', methods=['POST'])
def upgrade_upload():
    try: 
        originfile = request.files['file']
        print originfile.filename
        packagepath = "/opt"
        if not os.path.exists(packagepath):
            os.makedirs(packagepath)
        destfile = os.path.join(packagepath, originfile.filename)                                                                             
        with file(destfile, 'wb') as f:
            f.write(originfile.read())
        return ("success",200)
    except Exception as e:
        return ("error", 400)

  
@app.route('/prt')
def say():
    return "hello"

@app.route('/listCl')
def list():
    db = MySQLdb.connect(ip, user, password, database)
    cursor = db.cursor()
    sql = "select * from thinclient"
    cursor.execute(sql)
    result = cursor.fetchall()
    db.commit()
    db.close()
    clients = []
    for c in result:
        cl = Client()
        cl.mac = c[5]
        cl.ip = c[4]
        clients.append(cl.__dict__)
    return json.dumps(clients)

def getCid(mac):
    db = MySQLdb.connect(ip, user, password, database)
    cursor = db.cursor()
    sql = "select * from thinclient where mac='" + mac +"'"
    cursor.execute(sql)
    result = cursor.fetchone()
    cid = result[8]
    db.commit()
    db.close()
    return cid

@app.route('/say', methods=['get', 'post'])
def sayhello():
    try:
        transport_url = 'rabbit://guest:guest@10.0.0.108:5672/'  
        #transport_url = 'rabbit://guest:0082e5a4f6ab4a2e9096c4988110d67b@10.1.101.36:5672/'  
        transport = oslo_messaging.get_transport(cfg.CONF,transport_url)  
        #mac = request.args.get("mac")
        mac = request.json.get("mac")
        #mac = request.form["mac"]
        target = oslo_messaging.Target(topic='test', server=getCid(mac))  
        client = oslo_messaging.RPCClient(transport, target)  
        r = client.prepare(timeout=2).call({}, 'printTxt')  
    except:
        return ("error", 400)
    else:
        return 'success'

@app.route('/say2', methods=['get', 'post'])
def saygood():
    try:
            transport_url = 'rabbit://guest:guest@10.0.0.108:5672/'  
	    #transport_url = 'rabbit://guest:0082e5a4f6ab4a2e9096c4988110d67b@10.1.101.36:5672/'  
	    transport = oslo_messaging.get_transport(cfg.CONF,transport_url)  
	    #mac = request.args.get("mac")
	    mac = request.json.get("mac")
	    #mac = request.form["mac"]
	    target = oslo_messaging.Target(topic='test', server=getCid(mac))  
	    client = oslo_messaging.RPCClient(transport, target)  
	    r = client.prepare(timeout=2).call({}, 'sayGood')  
    except:
        return ("error", 400)
    else:
        return 'success'

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
