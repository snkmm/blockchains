from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only
from datetime import datetime
import sys

from models import Base, Order, Log
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

@app.before_request
def create_session():
    g.session = scoped_session(DBSession)

@app.teardown_appcontext
def shutdown_session(response_or_exc):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()


""" Suggested helper methods """

def check_sig(payload,sig):
    #same as Exchange Server I
    sk = sig

    #pk and platform in payload
    pk       = payload["pk"]
    platform = payload["platform"]

    #json form of payload
    msg = json.dumps(payload)

    #Check if signature is valid
    if (platform == "Ethereum"):
        eth_encoded_msg = eth_account.messages.encode_defunct(text=msg)
        eth_pk          = eth_account.Account.recover_message(eth_encoded_msg, signature=sk)
        return pk == eth_pk
    elif (platform == "Algorand"):
        alg_encoded_msg = msg.encode('utf-8')
        return algosdk.util.verify_bytes(alg_encoded_msg, sk, pk)
    return False

def fill_order(order,txes=[]):
    #same as Exchange Server II
    orders = g.session.query(Order).filter(Order.filled == None)
    for existing_order in orders:
        #check if there are any existing orders that match (1, 2, 3, and 4)
        if ((order.filled == None) \
        and (existing_order.buy_currency == order.sell_currency) \
        and (existing_order.sell_currency == order.buy_currency) \
        and (existing_order.sell_amount / existing_order.buy_amount >= order.buy_amount / order.sell_amount) \
        and (existing_order.sell_amount < order.buy_amount)):
            #check if a match is found between order and existing_order
            #set the filled field to be the current timestamp on both orders
            order.filled          = datetime.now()
            existing_order.filled = order.filled

            #set counterparty_id to be the id of the other order
            order.counterparty_id          = existing_order.id
            existing_order.counterparty_id = order.id

            #create a new order for remaining balance
            g.session.add(Order(
                #the new order should have the created_by field set to the id of its parent order
                creator_id    = order.id,
                buy_currency  = order.buy_currency,
                sell_currency = order.sell_currency,
                buy_amount    = order.buy_amount - existing_order.sell_amount,
                sell_amount   = order.sell_amount - existing_order.buy_amount,
                sender_pk     = order.sender_pk,
                receiver_pk   = order.receiver_pk
            ))
            g.session.commit()

def log_message(d):
    # Takes input dictionary d and writes it to the Log table
    # Hint: use json.dumps or str() to get it in a nice string form
    g.session.add(Log(message = json.dumps(d)))  #default: logtime = datetime.now()
    g.session.commit()

""" End of helper methods """



@app.route('/trade', methods=['POST'])
def trade():
    print("In trade endpoint")
    if request.method == "POST":
        content = request.get_json(silent=True)
        print( f"content = {json.dumps(content)}" )
        columns = [ "sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform" ]
        fields = [ "sig", "payload" ]

        for field in fields:
            if not field in content.keys():
                print( f"{field} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )

        for column in columns:
            if not column in content['payload'].keys():
                print( f"{column} not received by Trade" )
                print( json.dumps(content) )
                log_message(content)
                return jsonify( False )

        #Your code here
        #Note that you can access the database session using g.session
        #sig and payload in content
        sig     = content["sig"]
        payload = content["payload"]

        # TODO: Check the signature
        result = check_sig(payload, sig)

        # TODO: Add the order to the database
        #insert the order into the database
        order = Order(
            sender_pk     = payload["sender_pk"],
            receiver_pk   = payload["receiver_pk"],
            buy_currency  = payload["buy_currency"],
            sell_currency = payload["sell_currency"],
            buy_amount    = payload["buy_amount"],
            sell_amount   = payload["sell_amount"],
            signature     = content["sig"]
        )
        g.session.add(order)
        g.session.commit()

        # TODO: Fill the order
        fill_order(order)

        # TODO: Be sure to return jsonify(True) or jsonify(False) depending on if the method was successful
        if (result):
            return jsonify(True)
        return jsonify(False)

@app.route('/order_book')
def order_book():
    #Your code here
    #Note that you can access the database session using g.session
    #same as Exchange Server III
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
