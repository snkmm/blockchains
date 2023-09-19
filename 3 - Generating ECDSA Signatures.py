from fastecdsa.curve import secp256k1
from fastecdsa.keys import export_key, gen_keypair

from fastecdsa import curve, ecdsa, keys
from hashlib import sha256

def sign(m):
    #generate public key
    keypair     = gen_keypair(curve=secp256k1)
    private_key = keypair[0]  #or keys.gen_private_key(curve=secp256k1)
    public_key  = keypair[1]  #or keys.get_public_key(private_key, curve=secp256k1)

    #generate signature
    sign = ecdsa.sign(m, private_key, curve=secp256k1, hashfunc=sha256)
    r    = sign[0]
    s    = sign[1]
    return( public_key, [r,s] )
