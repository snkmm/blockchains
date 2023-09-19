from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models import Base, Order
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def process_order(order):
    #Your code here
    #insert the order into the database
    order = Order(
        buy_currency  = order["buy_currency"],
        sell_currency = order["sell_currency"],
        buy_amount    = order["buy_amount"],
        sell_amount   = order["sell_amount"],
        sender_pk     = order["sender_pk"],
        receiver_pk   = order["receiver_pk"]
    )
    session.add(order)
    session.commit()

    orders = session.query(Order).filter(Order.filled == None)
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
            session.add(Order(
                #the new order should have the created_by field set to the id of its parent order
                creator_id    = order.id,
                buy_currency  = order.buy_currency,
                sell_currency = order.sell_currency,
                buy_amount    = order.buy_amount - existing_order.sell_amount,
                sell_amount   = order.sell_amount - existing_order.buy_amount,
                sender_pk     = order.sender_pk,
                receiver_pk   = order.receiver_pk
            ))
            session.commit()
