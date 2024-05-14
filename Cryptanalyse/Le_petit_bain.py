import random as rd

charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789{}_-!"
n = len(charset)

def solve_equations(equations, n):
    x1, y1 = equations[0]
    x2, y2 = equations[1]
    
    a = pow(x1-x2, -1, n) * (y1-y2) % n
    b = (y1 - a*x1) % n
    
    return a, b

def unpermute(message):
    p = [2, 5, 1, 4, 0, 3, 8, 11, 7, 10, 6, 9, 14, 17, 13, 16, 12, 15, 20, 23, 19, 22, 18, 21, 26, 29, 25, 28, 24, 27, 32, 35, 31, 34, 30, 33, 38, 41, 37, 40, 36, 39, 44, 47, 43, 46, 42, 45]
    unpermuted = [''] * len(message)
    for i in range(len(message)):
        unpermuted[p[i]] = message[i]
    return ''.join(unpermuted)

def decrypt_round(ciphertext, A, B, n):
    decrypted = ""
    for i in range(len(ciphertext)):
        y = charset.index(ciphertext[i])
        a = A[i%6] 
        b = B[i%6]
        x = pow(a,-1,n) * (y - b) % n
        decrypted += charset[x]
    return unpermute(decrypted)

def solve_round(plaintext, ciphertext):
    A = []
    B = []
    for i in range(6):
        x1 = charset.index(plaintext[i])
        y1 = charset.index(ciphertext[i])
        x2 = charset.index(plaintext[i+6]) 
        y2 = charset.index(ciphertext[i+6])
        
        a = pow(x1-x2, -1, n) * (y1-y2) % n
        b = (y1 - a*x1) % n
        
        A.append(a)
        B.append(b)
        
    return A, B

def decrypt(ciphertext):
    known_plaintext = "404CTF{tHe_c"
    round6_ciphertext = ciphertext
    
    for i in range(6):
        A, B = solve_round(known_plaintext, round6_ciphertext[:12])
        round6_ciphertext = decrypt_round(round6_ciphertext, A, B, n)
        known_plaintext = round6_ciphertext[:12]
        
    return round6_ciphertext



ciphertext = "C_ef8K8rT83JC8I0fOPiN6P!liE03W2NXFh1viJCROAqXb6o"
flag = decrypt(ciphertext)
print(flag)

