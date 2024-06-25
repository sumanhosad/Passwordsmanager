from cryptography.fernet import Fernet
import base64
import random
import string


from cryptography.fernet import Fernet

def generate_key(hashed_mp):
    hashed_bytes = bytes.fromhex(hashed_mp)
    
    key = base64.urlsafe_b64encode(hashed_bytes)
    
    return key


def encrypt_message(website_details, mp):
    key = generate_key(mp)
    cipher_suite = Fernet(key)

    plaintext = ','.join(website_details)
    
    encrypted_message = cipher_suite.encrypt(plaintext.encode())
    return encrypted_message

def decrypt_message(encrypted_message, mp):
    key = generate_key(mp)
    cipher_suite = Fernet(key)

    decrypted_message = cipher_suite.decrypt(encrypted_message).decode()

    website_details = decrypted_message.split(',')
    return website_details

def concatenate_sublists(sublists):
    return [item for sublist in sublists for item in sublist]

def split_into_sublists(main_list, sublist_size=5):
    return [main_list[i:i + sublist_size] for i in range(0, len(main_list), sublist_size)]
