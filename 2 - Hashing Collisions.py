import hashlib
import os

def hash_collision(k):
    if not isinstance(k,int):
        print( "hash_collision expects an integer" )
        return( b'\x00',b'\x00' )
    if k <= 0:
        print( "Specify a positive number of bits" )
        return( b'\x00',b'\x00' )

    #Collision finding code goes here
    x = b'\x00'
    y = b'\x00'

    list_dict = {}
    size = 16
    while True:
        #generate a string of size random bytes
        x_byte = os.urandom(size)
        y_byte = os.urandom(size)

        #calculate SHA256(x_byte) and SHA256(y_byte), and return binary values
        h_hex = hashlib.sha256( x_byte ).hexdigest()
        x_bin = bin( int( h_hex, base=16 ) )[-k:]
        h_hex = hashlib.sha256( y_byte ).hexdigest()
        y_bin = bin( int( h_hex, base=16 ) )[-k:]

        #check if x_bin are in the list
        if x_bin in list_dict.values():
            for y_key, y_val in list_dict.items():
                #check if x_bin and y_val match
                if x_bin == y_val:
                    x, y = x_byte, y_key
            break
        else:
            #update the dictionaries
            list_dict.update([(x_byte, x_bin), (y_byte, y_bin)])

    return( x, y )
