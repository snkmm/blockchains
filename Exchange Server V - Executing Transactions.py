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
import math
import sys
import traceback

from algosdk import mnemonic
from algosdk import account
from web3 import Web3

# TODO: make sure you implement connect_to_algo, send_tokens_algo, and send_tokens_eth
from send_tokens import connect_to_algo, connect_to_eth, send_tokens_algo, send_tokens_eth

from models import Base, Order, TX, Log
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)

""" Pre-defined methods (do not need to change) """

@app.before_request
def create_session():
    g.session = scoped_session(DBSession)

@app.teardown_appcontext
def shutdown_session(response_or_exc):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()

def connect_to_blockchains():
    try:
        # If g.acl has not been defined yet, then trying to query it fails
        acl_flag = False
        g.acl
    except AttributeError as ae:
        acl_flag = True

    try:
        if acl_flag or not g.acl.status():
            # Define Algorand client for the application
            g.acl = connect_to_algo()
    except Exception as e:
        print("Trying to connect to algorand client again")
        print(traceback.format_exc())
        g.acl = connect_to_algo()

    try:
        icl_flag = False
        g.icl
    except AttributeError as ae:
        icl_flag = True

    try:
        if icl_flag or not g.icl.health():
            # Define the index client
            g.icl = connect_to_algo(connection_type='indexer')
    except Exception as e:
        print("Trying to connect to algorand indexer client again")
        print(traceback.format_exc())
        g.icl = connect_to_algo(connection_type='indexer')


    try:
        w3_flag = False
        g.w3
    except AttributeError as ae:
        w3_flag = True

    try:
        if w3_flag or not g.w3.isConnected():
            g.w3 = connect_to_eth()
    except Exception as e:
        print("Trying to connect to web3 again")
        print(traceback.format_exc())
        g.w3 = connect_to_eth()

""" End of pre-defined methods """

""" Helper Methods (skeleton code for you to implement) """

def log_message(message_dict):
    msg = json.dumps(message_dict)

    # TODO: Add message to the Log table
    g.session.add(Log(message = msg))  #default: logtime = datetime.now()
    g.session.commit()
    return

def get_algo_keys():

    # TODO: Generate or read (using the mnemonic secret)
    # the algorand public/private keys
    mnemonic_secret = "hire gauge depth relief room move fish bring arena magnet tennis mimic lens dress glad guess twist crash script girl make lottery dilemma absorb spice"
    algo_sk = mnemonic.to_private_key(mnemonic_secret)
    algo_pk = mnemonic.to_public_key(mnemonic_secret)
    return algo_sk, algo_pk


def get_eth_keys(filename = "eth_mnemonic.txt"):
    w3 = Web3()

    # TODO: Generate or read (using the mnemonic secret)
    # the ethereum public/private keys
    w3.eth.account.enable_unaudited_hdwallet_features()
    mnemonic_secret = "produce calm goose guilt design rubber limb catalog federal town voice saddle"
    acct = w3.eth.account.from_mnemonic(mnemonic_secret)
    eth_pk = acct._address
    eth_sk = acct._private_key
    return eth_sk, eth_pk

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

def fill_order(order, txes=[]):
    # TODO:
    # Match orders (same as Exchange Server II)
    # Validate the order has a payment to back it (make sure the counterparty also made a payment)
    # Make sure that you end up executing all resulting transactions!
    orders = g.session.query(Order).filter(Order.filled == None)
    for existing_order in orders:
        #check if there are any existing orders that match (1, 2, 3, and 4)
        if ((order.filled == None) \
        and (existing_order.buy_currency == order.sell_currency) \
        and (existing_order.sell_currency == order.buy_currency) \
        and (existing_order.sell_amount / existing_order.buy_amount >= order.buy_amount / order.sell_amount) \
        and (existing_order.sell_amount < order.buy_amount) \
        and (existing_order.sell_amount == order.sell_amount)):
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

            #create a new TX
            g.session.add(TX(
                platform    = order.sell_currency,
                receiver_pk = order.receiver_pk,
                order_id    = order.id,
                tx_id       = order.tx_id
            ))
            g.session.commit()

def execute_txes(txes):
    if txes is None:
        return True
    if len(txes) == 0:
        return True
    print( f"Trying to execute {len(txes)} transactions" )
    print( f"IDs = {[tx['order_id'] for tx in txes]}" )
    eth_sk, eth_pk = get_eth_keys()
    algo_sk, algo_pk = get_algo_keys()

    if not all( tx['platform'] in ["Algorand","Ethereum"] for tx in txes ):
        print( "Error: execute_txes got an invalid platform!" )
        print( tx['platform'] for tx in txes )

    algo_txes = [tx for tx in txes if tx['platform'] == "Algorand" ]
    eth_txes = [tx for tx in txes if tx['platform'] == "Ethereum" ]

    # TODO:
    #       1. Send tokens on the Algorand and eth testnets, appropriately
    #          We've provided the send_tokens_algo and send_tokens_eth skeleton methods in send_tokens.py
    #       2. Add all transactions to the TX table

    pass

""" End of Helper methods"""

@app.route('/address', methods=['POST'])
def address():
    if request.method == "POST":
        content = request.get_json(silent=True)
        if 'platform' not in content.keys():
            print( f"Error: no platform provided" )
            return jsonify( "Error: no platform provided" )
        if not content['platform'] in ["Ethereum", "Algorand"]:
            print( f"Error: {content['platform']} is an invalid platform" )
            return jsonify( f"Error: invalid platform provided: {content['platform']}"  )

        if content['platform'] == "Ethereum":
            #Your code here
            _, eth_pk = get_eth_keys()
            return jsonify( eth_pk )
        if content['platform'] == "Algorand":
            #Your code here
            _, algo_pk = get_algo_keys()
            return jsonify( algo_pk )

@app.route('/trade', methods=['POST'])
def trade():
    print( "In trade", file=sys.stderr )
    connect_to_blockchains()
    #get_keys()
    if request.method == "POST":
        content = request.get_json(silent=True)
        columns = [ "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform", "tx_id", "receiver_pk"]
        fields = [ "sig", "payload" ]
        error = False
        for field in fields:
            if not field in content.keys():
                print( f"{field} not received by Trade" )
                error = True
        if error:
            print( json.dumps(content) )
            return jsonify( False )

        error = False
        for column in columns:
            if not column in content['payload'].keys():
                print( f"{column} not received by Trade" )
                error = True
        if error:
            print( json.dumps(content) )
            return jsonify( False )

        # Your code here
        #sig and payload in content
        sig     = content["sig"]
        payload = content["payload"]

        # 1. Check the signature
        result = check_sig(payload, sig)

        # 2. Add the order to the table
        order = Order(
            sender_pk     = payload["sender_pk"],
            receiver_pk   = payload["receiver_pk"],
            buy_currency  = payload["buy_currency"],
            sell_currency = payload["sell_currency"],
            buy_amount    = payload["buy_amount"],
            sell_amount   = payload["sell_amount"],
            signature     = sig,
            tx_id         = payload["tx_id"]
        )
        g.session.add(order)
        g.session.commit()

        # 3a. Check if the order is backed by a transaction equal to the sell_amount (this is new)
        # 3b. Fill the order (as in Exchange Server II) if the order is valid
        txes = fill_order(order)

        # 4. Execute the transactions
        execute_txes(txes)

        # If all goes well, return jsonify(True). else return jsonify(False)
        if (result):
            return jsonify(True)
        else:
            log_message(content)
            return jsonify(False)

@app.route('/order_book')
def order_book():
    fields = [ "buy_currency", "sell_currency", "buy_amount", "sell_amount", "signature", "tx_id", "receiver_pk" ]

    # Same as before
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
        order_dict["tx_id"]         = order.tx_id
        order_list.append(order_dict)
    return jsonify(data=order_list)

if __name__ == '__main__':
    app.run(port='5002')
