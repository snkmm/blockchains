from web3 import Web3
from hexbytes import HexBytes

IP_ADDR='18.188.235.196'
PORT='8545'

w3 = Web3(Web3.HTTPProvider('http://' + IP_ADDR + ':' + PORT))

'''
if w3.isConnected():
    print( "Connected to Ethereum node" )
else:
    print( "Failed to connect to Ethereum node!" )
'''

def get_transaction(tx):
    #YOUR CODE HERE
    tx = w3.eth.get_transaction(tx)
    return tx

# Return the gas price used by a particular transaction,
#   tx is the transaction
def get_gas_price(tx):
    #YOUR CODE HERE
    gas_price = w3.eth.get_transaction(tx)["gasPrice"]
    return gas_price

def get_gas(tx):
    #YOUR CODE HERE
    gas = w3.eth.get_transaction_receipt(tx)["gasUsed"]
    return gas

def get_transaction_cost(tx):
    #YOUR CODE HERE
    tx_cost = get_gas_price(tx) * get_gas(tx)
    return tx_cost

def get_block_cost(block_num):
    #YOUR CODE HERE
    transactions = w3.eth.get_block(block_num)["transactions"]

    block_cost = 0
    for i in transactions:
        block_cost += get_transaction_cost(i)
    return block_cost

# Return the hash of the most expensive transaction
def get_most_expensive_transaction(block_num):
    #YOUR CODE HERE
    transactions = w3.eth.get_block(block_num)["transactions"]

    max_cost = 0
    max_tx   = HexBytes('******************************************************************')
    for i in transactions:
        cost = get_transaction_cost(i)
        if (cost > max_cost):
            max_cost = cost
            max_tx   = i
    return max_tx
