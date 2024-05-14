import numpy as np

url = r"challenge"
def decode_data(encoded_data):
    data = encoded_data[:-1]
    parity_bit = encoded_data[-1]
    if sum(data)%2 != parity_bit:
        data[3] = 1 - data[3]  # Correction du bit du canal 4 si parité incorrecte
    return data

def decode_file():
    channels = []
    for i in range(1,9):
        with open(url + "\\" + f"channel_{i}","r") as f:
            channel = np.array(list(f.read()), dtype="uint8")
            channels.append(channel)
    
    data_bits = []
    for i in range(len(channels[0])):
        encoded_byte = [channels[j][i] for j in range(8)]
        decoded_byte = decode_data(encoded_byte)
        data_bits.extend(decoded_byte)
    
    data_bytes = np.packbits(np.array(data_bits))
    
    with open(url + "\\" +"decoded_flag.png","wb") as f:
        f.write(data_bytes.tobytes())

decode_file()
