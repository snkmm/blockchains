from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine, select, MetaData, Table
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only

from models import Base, Order, Log
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

#These decorators allow you to use g.session to access the database inside the request code
@app.before_request
def create_session():
    g.session = scoped_session(DBSession) #g is an "application global" https://flask.palletsprojects.com/en/1.1.x/api/#application-globals

@app.teardown_appcontext
def shutdown_session(response_or_exc):
    g.session.commit()
    g.session.remove()

"""
-------- Helper methods (feel free to add your own!) -------
"""

def log_message(d):
    # Takes input dictionary d and writes it to the Log table
    g.session.add(Log(message = d))  #default: logtime = datetime.now()
    g.session.commit()
"""
---------------- Endpoints ----------------
"""

@app.route('/trade', methods=['POST'])
def trade():
    if request.method == "POST":
        content = request.get_json(silent=True)
        print( f"content = {json.dumps(content)}" )
        columns = [ "sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform" ]
        fields = [ "sig", "payload" ]
        error = False
        for field in fields:
            if not field in content.keys():
                print( f"{field} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )

        error = False
        for column in columns:
            if not column in content['payload'].keys():
                print( f"{column} not received by Trade" )
                error = True
        if error:
            print( json.dumps(content) )
            log_message(content)
            return jsonify( False )

        #Your code here
        #Note that you can access the database session using g.session
        #payload in content
        payload = content["payload"]

        #insert the order into the database
        g.session.add(Order(
            sender_pk     = payload["sender_pk"],
            receiver_pk   = payload["receiver_pk"],
            buy_currency  = payload["buy_currency"],
            sell_currency = payload["sell_currency"],
            buy_amount    = payload["buy_amount"],
            sell_amount   = payload["sell_amount"],
            signature     = content["sig"]
        ))
        g.session.commit()
        return jsonify( True )

@app.route('/order_book')
def order_book():
    #Your code here
    #Note that you can access the database session using g.session
    #return a list of all orders in the database
    order_list = []
    orders     = g.session.query(Order)
    for order in orders:
        order_dict = {}
        order_dict["sender_pk"]     = order.sender_pk
        order_dict["receiver_pk"]   = order.receiver_pk
        order_dict["buy_currency"]  = order.buy_currency
        order_dict["sell_currency"] = order.sell_currency
        order_dict["buy_amount"]    = order.buy_amount
        order_dict["sell_amount"]   = order.sell_amount
        order_dict["signature"]     = order.signature
        order_list.append(order_dict)
    return jsonify(data=order_list)

if __name__ == '__main__':
    app.run(port='5002')
