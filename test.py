import os
import ipfsclient

client = ipfsclient.connect('https://ipfs11.rocknblock.io', 443)

add_hash = client.add_file(os.path.dirname(__file__) + '/13.png')
print(add_hash)

get_hash = client.get(add_hash)
print(get_hash)
