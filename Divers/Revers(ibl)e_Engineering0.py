import os
from zipfile import ZipFile
from pwn import *
import pwnlib.tubes.process
import time
import ctypes
import subprocess
import random
import string
import itertools

TOKEN = ""
LOCAL_28 = 0x1
LOCAL_20 = 0x1
directory_path = r'/home/kali/Documents/ctfcinfile'
zip_file_path = os.path.join(directory_path, 'chall.zip')
crackme_path = os.path.join(directory_path, 'crackme.bin')
token_file_path = os.path.join(directory_path, 'token.txt')

def dl():
    global TOKEN
    # Vérification de l'existence du dossier et création s'il n'existe pas
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    # Vérification de l'existence du fichier zip et suppression si nécessaire
    if os.path.exists(zip_file_path):
        os.remove(zip_file_path)
        print(f"Le fichier {zip_file_path} existant a été supprimé.")
    
    # Configuration de la connexion
    host = "challenges.404ctf.fr"
    port = 31998
    
    # Connexion au serveur et récupération des données
    try:
        conn = remote(host, port)
        data = conn.recvall()

        # Enregistrement des données dans un fichier zip
        with open(zip_file_path, 'wb') as f:
            f.write(data)
            print(f"Fichier {zip_file_path} téléchargé et enregistré avec succès.")
        
        # Dézipper le fichier
        with ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(directory_path)
            print("Fichier dézippé.")
        
        # Suppression du fichier zip
        os.remove(zip_file_path)
        print(f"Fichier {zip_file_path} supprimé après extraction.")

        # Lire et afficher le contenu de token.txt
        token_file_path = os.path.join(directory_path, 'token.txt')
        with open(token_file_path, 'r') as token_file:
            TOKEN = token_file.read()
            print("Contenu de token.txt:", TOKEN)
            
        crackme_file_path = os.path.join(directory_path, 'crackme.bin')
        os.chmod(crackme_file_path, 0o755)
        print(f"Permissions changées pour {crackme_file_path}.")
        

    except Exception as e:
        print(f"Une erreur est survenue lors de la connexion ou du téléchargement: {e}")




def disassemble_binary(file_path):
    global LOCAL_28, LOCAL_20
    # Ouvrir le fichier en mode lecture binaire
    with open(file_path, 'rb') as file:
        data = file.read()

    # Afficher tout le contenu du fichier en hexadécimal avec les offsets standard
    print("Contenu complet en hexadécimal avec offsets:")
    for i in range(0, len(data), 16):  # Afficher 16 octets par ligne
        line_data = data[i:i+16]
        #print(f"{i:08x}: {line_data.hex()}")

    # Rechercher les séquences spécifiques et traiter les données
    index = 0
    while index < len(data) - 18:  # S'assurer qu'il reste assez de données pour la capture
        # Chercher la séquence 48b8 et 48ba
        if data[index:index+2] == b'\x48\xb8':
            start = index + 2
            if start + 8 <= len(data):
                values = data[start:start+8]
                #reversed_values = values[::-1]
                reversed_hex = ''.join(f"{byte:02x}" for byte in values)
                print(f"\nSéquence 48b8 trouvée à l'offset {index:08x}, valeurs inversées: 0x{reversed_hex}")
                LOCAL_28 = reversed_hex
        
        if data[index:index+2] == b'\x48\xba':
            start = index + 2
            if start + 8 <= len(data):
                values = data[start:start+8]
                #reversed_values = values[::-1]
                reversed_hex = ''.join(f"{byte:02x}" for byte in values)
                print(f"Séquence 48ba trouvée à l'offset {index:08x}, valeurs inversées: 0x{reversed_hex}")
                LOCAL_20 = reversed_hex

        index += 1  # Mettre à jour l'index pour continuer la recherche


def get_rax_value(binary, input_string):

    gdb_commands = [
        f'file {binary}',
        'b puts',
        f'run {input_string}',
        'x/2x 0x5555555592a0',
        'quit'
    ]

    gdb_process = subprocess.Popen(['gdb', '--quiet'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    gdb_output, _ = gdb_process.communicate('\n'.join(gdb_commands))

    for line in gdb_output.split('\n'):
        if 'gdb-peda$' in line and line.count('0x') == 3:
            hex_values = line.split(':')[1].strip().replace("0x","").replace(" ","")
            
            hex_v1 = hex_values.split("\t")[0]
            octets = [hex_v1[i:i+2] for i in range(0, len(hex_v1), 2)]
            octets.reverse()
            hex_v1 = ''.join(octets)
            
            hex_v2 = hex_values.split("\t")[1]
            octets = [hex_v2[i:i+2] for i in range(0, len(hex_v2), 2)]
            octets.reverse()
            hex_v2 = ''.join(octets)
            
            
            return hex_v1 + hex_v2

    print("pb adresse")
    exit(1)


def trouver_mot_de_passe(hash_cible):
    texte = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    dictionnaire = {caractere: '' for caractere in texte}
    
    for i in range(0, len(texte), 16):
        groupe = texte[i:i+16]
        if len(groupe) < 16:
            groupe += 'a' * (16 - len(groupe))
        
        hexa = get_rax_value(crackme_path, groupe)
        for index, caractere in enumerate(groupe):
            if index < 16:  # S'assurer de ne pas dépasser la longueur de la chaîne hexa
                dictionnaire[caractere] = hexa[index*2:index*2+2]
    print(dictionnaire)
    dictionnaire_inverse = {valeur: cle for cle, valeur in dictionnaire.items() if valeur}

    # Reconstruire le mot à partir de hash_cible
    mdp = ""
    for i in range(0, len(hash_cible), 2):
        hex_pair = hash_cible[i:i+2]
        if hex_pair in dictionnaire_inverse:
            mdp += dictionnaire_inverse[hex_pair]
        else:
            mdp += '?'
    return mdp
            
def envoyer_token(token, mdp):
    conn = remote("challenges.404ctf.fr", 31999)
    

    # Attendre et lire la réponse jusqu'à ce que "Token ?" soit reçu
    conn.recvuntil(b"Token ?")
    
    # Envoi du token
    print("\nEnvoi du token...")
    conn.sendline(token.encode())
    
    # Attendre et lire la réponse jusqu'à ce que "Alors, la solution ?" soit reçu
    conn.recvuntil(b"Alors, la solution ?")
    
    # Envoi du mot de passe
    print("\nEnvoi du mot de passe...")
    conn.sendline(mdp.encode())
    
    # Recevoir et afficher la réponse finale après l'envoi du mot de passe
    reponse_finale = conn.recvall().decode('utf-8')
    print(reponse_finale.strip())
 
    conn.close()
    
    
def main():
    global LOCAL_28, LOCAL_20, TOKEN
    dl()
    disassemble_binary(crackme_path)
    
    print("encrypted_value : ",LOCAL_28,LOCAL_20)
    mdp = trouver_mot_de_passe(LOCAL_28+LOCAL_20)
    print(mdp, TOKEN)
    envoyer_token(TOKEN, mdp)
    
  

main()

