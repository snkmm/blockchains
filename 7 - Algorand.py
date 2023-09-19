#!/usr/bin/python3

from algosdk.v2client import algod
from algosdk import mnemonic
from algosdk import transaction

#Connect to Algorand node maintained by PureStake
algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "****************************************"

headers = {
   "X-API-Key": algod_token,
}

acl = algod.AlgodClient(algod_token, algod_address, headers)
min_balance = 100000 #https://developer.algorand.org/docs/features/accounts/#minimum-balance

def send_tokens( receiver_pk, tx_amount ):
    params = acl.suggested_params()
    gen_hash = params.gh
    first_valid_round = params.first
    tx_fee = params.min_fee
    last_valid_round = params.last

    #Your code here
    #generate an account
    mnemonic_secret = "hire gauge depth relief room move fish bring arena magnet tennis mimic lens dress glad guess twist crash script girl make lottery dilemma absorb spice"
    sk = mnemonic.to_private_key(mnemonic_secret)
    pk = mnemonic.to_public_key(mnemonic_secret)

    #create a Payment Transaction
    tx = transaction.PaymentTxn(pk,
                                tx_fee,
                                first_valid_round,
                                last_valid_round,
                                gen_hash,
                                receiver_pk,
                                tx_amount)

    #sign the transaction with your secret key
    tx_sign = tx.sign(sk)

    #send the signed transaction to the blockchain
    txid = acl.send_transaction(tx_sign)

    #rename pk
    sender_pk = pk

    return sender_pk, txid

# Function from Algorand Inc.
def wait_for_confirmation(client, txid):
    """
    Utility function to wait until the transaction is
    confirmed before proceeding.
    """
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo
