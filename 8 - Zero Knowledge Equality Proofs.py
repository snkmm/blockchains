from zksk import Secret, DLRep
from zksk import utils

def ZK_equality(G,H):
    #Three secrets r1, r2, and m
    r1   = Secret(utils.get_random_num(bits=128))
    r2   = Secret(utils.get_random_num(bits=128))
    m    = Secret(utils.get_random_num(bits=2))  #m = 0 or 1
    r1_v = r1.value
    r2_v = r2.value
    m_v  = m.value

    #Generate two El-Gamal ciphertexts (C1,C2) and (D1,D2)
    C1 = r1_v * G
    C2 = r1_v * H + m_v * G
    D1 = r2_v * G
    D2 = r2_v * H + m_v * G

    #Generate a NIZK proving equality of the plaintexts
    stmt     = DLRep(C1, r1 * G) & DLRep(C2, r1 * H + m * G) & \
               DLRep(D1, r2 * G) & DLRep(D2, r2 * H + m * G)
    zk_proof = stmt.prove()

    #Return two ciphertexts and the proof
    return (C1,C2), (D1,D2), zk_proof
