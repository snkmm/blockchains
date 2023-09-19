def encrypt(key,plaintext):
    ciphertext=""
    #YOUR CODE HERE
    #ASCII value for character "A"
    a_asc = ord("A")
    #make sure that string is all in upper case
    plaintext = plaintext.upper()
    for i in range(len(plaintext)):
        #character to integer
        temp_int = ord(plaintext[i]) + key - a_asc
        #integer to character
        ciphertext += chr(temp_int % 26 + a_asc)
    return ciphertext

def decrypt(key,ciphertext):
    plaintext=""
    #YOUR CODE HERE
    #ASCII value for character "A"
    a_asc = ord("A")
    #make sure that string is all in upper case
    ciphertext = ciphertext.upper()
    for i in range(len(ciphertext)):
        #character to integer
        temp_int = ord(ciphertext[i]) - key - a_asc
        #integer to character
        plaintext += chr(temp_int % 26 + a_asc)
    return plaintext
