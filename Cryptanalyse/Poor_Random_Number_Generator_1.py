import os
from Cryptodome.Util.number import long_to_bytes
from Cryptodome.Util.number import long_to_bytes

class Generator:

    def __init__(self):
        self.feed = [int.from_bytes(os.urandom(1), byteorder='big') for i in range(2000)]
        
    def get_next_byte(self):
        number = 0

        for i in range(len(self.feed)):
            if i%2==0:
                number += pow(self.feed[i],i,2**8) + self.feed[i]*i
                number = ~number
            else:
                number ^= self.feed[i]*i+i


        number %= 2**8
        self.feed = self.feed[1:]
        self.feed.append(number)
        return number

    def get_random_bytes(self,length):
        random = b''

        for i in range(length):
            random += long_to_bytes(self.get_next_byte())

        return random
	
def xor(b1, b2):
    return bytes(a ^ b for a, b in zip(b1, b2))

# Lecture des données chiffrées et partiellement en clair
with open("flag.png.enc", "rb") as f:
    encrypted_data = f.read()

with open("flag.png.part", "rb") as f:  
    partial_clear = f.read()

# Taille de bloc utilisée pour le chiffrement
BLOCK_SIZE = 4

# Récupération du keystream partiel par XOR du clair et du chiffré
partial_keystream = xor(partial_clear, encrypted_data[:len(partial_clear)])

# Reconstruction de l'état interne du PRNG
leaked_numbers = []
for i in range(0, len(partial_keystream), BLOCK_SIZE):
    leaked_numbers.extend(partial_keystream[i:i+BLOCK_SIZE])

generator = Generator()
for i in range(len(leaked_numbers)):
    generator.get_next_byte()
    generator.feed[-1] = leaked_numbers[i]

# Déchiffrement du reste des données
decrypted_data = partial_clear

for i in range(len(partial_clear), len(encrypted_data), BLOCK_SIZE):
    keystream_block = generator.get_random_bytes(BLOCK_SIZE)
    decrypted_block = xor(encrypted_data[i:i+BLOCK_SIZE], keystream_block)
    decrypted_data += decrypted_block

# Écriture du fichier déchiffré  
with open("flag.png", "wb") as f:
    f.write(decrypted_data)
