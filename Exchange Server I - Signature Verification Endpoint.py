from flask import Flask, request, jsonify
from flask_restful import Api
import json
import eth_account
import algosdk

app = Flask(__name__)
api = Api(app)
app.url_map.strict_slashes = False

@app.route('/verify', methods=['GET','POST'])
def verify():
    content = request.get_json(silent=True)

    #sig and payload in content
    sk      = content["sig"]
    payload = content["payload"]

    #pk and platform in payload
    pk       = payload["pk"]
    platform = payload["platform"]

    #json form of payload
    msg = json.dumps(payload)

    #Check if signature is valid
    if (platform == "Ethereum"):
        eth_encoded_msg = eth_account.messages.encode_defunct(text=msg)
        eth_pk          = eth_account.Account.recover_message(eth_encoded_msg, signature=sk)
        return jsonify(pk == eth_pk)
    elif (platform == "Algorand"):
        alg_encoded_msg = msg.encode('utf-8')
        return jsonify(algosdk.util.verify_bytes(alg_encoded_msg, sk, pk))
    return jsonify(False)

if __name__ == '__main__':
    app.run(port='5002')
