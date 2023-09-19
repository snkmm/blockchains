import random

from params import p
from params import g

def keygen():
    #pick a random "a" in the range 1 < a < p
    a = random.SystemRandom().randint(2, p - 1)

    #set h = g^a mod p
    h = pow(g, a, p)

    sk = a
    pk = h
    return pk,sk

def encrypt(pk,m):
    #public key "h"
    h = pk

    #pick a random "r" in the range 1 < r < p
    r = random.SystemRandom().randint(2, p - 1)

    #set (c1, c2) = (g^r mod p, h^r * m mod p)
    c1 = pow(g, r, p)
    c2 = pow(pow(h, r, p) * m, 1, p)
    return [c1,c2]

def decrypt(sk,c):
    #secret key "a"
    a = sk

    #from "rsa_util" on the optional homework "RSA encryption"
    def mod_inverse(a, m):
        x, y = 1, 0
        while (a > 1):
            q = a // m
            t = m
            m = a % m
            a = t
            t = y
            y = x - q * y
            x = t
        return x

    #calculate m = c2 / c1^a mod p
    c2      = pow(c[1], 1, p)
    c1a_div = pow(mod_inverse(c[0], p), a, p)
    
    m = pow(c2 * c1a_div, 1, p)
    return m
