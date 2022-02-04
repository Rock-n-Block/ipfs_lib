import os

import ipfsclient

client = ipfsclient.connect(endpoint="https://ipfs11.rocknblock.io", port=443)


with client as session:
    add_hash = session.add(
        file=os.path.dirname(__file__) + "/13.png",
        params={"pin": True, "quieter": True},
    )
    print(add_hash)

    hash = session.add_json(json_obj={"akuna": "matata"})
    print(hash)
    print(session.get_json(hash))

    hash = session.add_str(string="Hello World!")
    print(hash)
    print(session.get_str(hash))
