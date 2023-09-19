import hashlib
import os

def hash_preimage(target_string):
    if not all( [x in '01' for x in target_string ] ):
        print( "Input should be a string of bits" )
        return
    nonce = b'\x00'

    #the length of target_string
    k = len(target_string)
    while True:
        #generate a string of size random bytes
        x_byte = os.urandom(k)

        #calculate SHA256(x_byte), and return binary value
        h_hex = hashlib.sha256( x_byte ).hexdigest()
        x_bin = bin( int( h_hex, base=16 ) )[-k:]

        #check if x_bin and target_string match
        if x_bin == target_string:
            nonce = x_byte
            break

    return( nonce )
