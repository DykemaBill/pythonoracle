import sys
from cryptography.fernet import Fernet

# Generate encryption key
def passkey():
    # Generate key
    key = Fernet.generate_key()
    # Decoded encryption key to be stored
    keyDecoded = key.decode("utf-8")
    return keyDecoded

# Encrypt password using key
def passencrypt(mykey, mypassword):
    # Take key from stored form and convert it back to byte form
    keyRecovered = mykey.encode("utf-8")
    encryptKeyRecovered = Fernet(keyRecovered)
    # Encrypt password from byte form with str.encode
    encryptPass = encryptKeyRecovered.encrypt(str.encode(mypassword))
    # Decode encrypted password to string form to be stored
    encryptPassDecoded = encryptPass.decode("utf-8")
    return encryptPassDecoded

# Decrypt password using key
def passdecrypt(mykey, mypasswordencrypted):
    # Take key from stored form and convert it back to byte form
    keyRecovered = mykey.encode("utf-8")
    encryptKeyRecovered = Fernet(keyRecovered)
    # Using recovered key unencrypt stored password
    encryptPassEncode = mypasswordencrypted.encode("utf-8")
    originalPassByte = encryptKeyRecovered.decrypt(encryptPassEncode)
    originalPass = originalPassByte.decode("utf-8")
    return originalPass

# Get command line arguments
if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "key":
        yourKey = passkey()
        print ("Here is your encryption key:", yourKey)
    elif len(sys.argv) == 4 and sys.argv[1] == "encrypt":
        yourPassEncrypted = passencrypt(sys.argv[2], sys.argv[3])
        print ("Here is your encrypted password:", yourPassEncrypted)
    elif len(sys.argv) == 4 and sys.argv[1] == "decrypt":
        yourPass = passdecrypt(sys.argv[2], sys.argv[3])
        print ("Here is your password:", yourPass)
    else:
        print ("Syntax:")
        print ("        " + sys.argv[0] + " key")
        print ("          Run with the word key to recieve a key")
        print ("        " + sys.argv[0] + " encrypt [key] [password]")
        print ("          Send a valid key along with a password to receive an encrypted version")
        print ("        " + sys.argv[0] + " decrypt [key] [password]")
        print ("          Send a valid key along with an encrypted password to receive the original password")