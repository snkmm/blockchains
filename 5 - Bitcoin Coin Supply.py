import math

def num_BTC(b):
    c = float(0)

    # set h = 210000
    h = 210000

    # block reward was initially 50 BTC
    r = 50
    i = 0
    while (i < b):
        # 50 BTC at Block 1, 100 BTC at Block 2, and so on
        c += r
        i += 1

        # reward halves every h blocks
        ih = pow(i, 1, h)
        if (ih == 0):
            r /= 2
    return c
