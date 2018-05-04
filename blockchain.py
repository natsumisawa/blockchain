# coding:utf-8

import hashlib
import json
from textwrap import dedent
from urlparse import urlparse
from time import time
from uuid import uuid4

import requests
from flask import Flask, jsonify, request

class Blockchain(object):
    def __init__(self):
        # ブロックチェーンを収めるための空リスト
        self.chain = []
        # トランザクションを収めるための空リスト
        self.current_transactions = []

        # ジェネシスブロックを作る
        self.new_block(previous_hash=1, proof=100)

        # ノードをリストを保持するためのセット、重複を許さないようにするため
        self.nodes = set()

    def new_block(self, proof, previous_hash=None):
        """ブロックチェーンに新しいブロックを作る
        :param proof: <int> プルーフ・オブ・ワークアルゴリズムから得られるプルーフ
        :param previous_hash:  (オプション) <str> 前のブロックのハッシュ
        :return: <dict> 新しいブロック"""

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # 現在のトランザクションリストをリセット
        self.current_transactions = []

        self.chain.append(block)
        return block

    def register_node(self, address):
        """
        ノードリストに新しいノードを加える
        :param address: <str> ノードのアドレス
        :return: None
        """

        parse_url = urlparse(address)
        self.nodes.add(parse_url.netloc)

    # 新しいトランザクションをリストに加える
    def new_transaction(self):
        pass

    # ブロックをハッシュ化する
    @staticmethod
    def hash(block):
        """
        ブロックのSHA-256ハッシュを作る
        :param block: <dict> ブロック
        :return: <str<
        """

        # 必ず辞書型オブジェクトがソートされている必要がある、そうでないと一貫性のないハッシュとなってしまう
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    # チェーンの最後のブロックをリターンする
    @property
    def last_block(self):
        return self.chain[-1]

    #  新しいトランザクションをリストに加え、そのトランザクションが加えられるブロックのインデックスを返す
    def new_transaction(self, sender, recipient, amount):
        """
        次に採用されるブロックに加える新しいトランザクションを作る
        :param sender: <str> 送信者のアドレス
        :param recipient: <str> 受信者のアドレス
        :param amount: <int> 量
        :return: <int> このトランザクションを含むブロックのアドレス
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        """
        シンプルなプルーフ・オブ・ワークのアルゴリズム:
        - hash(pp')の最初の4つが0となるようなp'を探す
        - p は一つ前のブロックのプルーフ、p'は新しいブロックのプルーフ
        :param last_proof: <int>
        :return: <int>
        """
        proof = 0

        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """プルーフが正しいかを確認する: hash(last_proof, proof)の最初の4つが0となっているか
        :param last_proof: <int> 前のプルーフ
        :param proof: <int> 現在のプルーフ
        :return: <bool> 正しければ true, そうでなければ false
        """

        guess = '{last_proof}{proof}'.format(last_proof = last_proof, proof = proof).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:4] == "0000"

    def valid_chain(self, chain):
        """チェーンの中のすべてのブロックに対してハッシュとプルーフが正しいかを確認することで、ブロックチェーンが正しいかを確認する。
        :param cahin: <list> ブロックチェーン
        :return: <bool> Trueであれば正しく、Falseであればそうではない"""

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print({last_block})
            print(block)
            print("\n--------------\n")

            # ブロックのハッシュが正しいかどうかを確認
            if block['previous_hash'] != self.hash(last_block):
                return False

            # プルーフ・オブ・ワークが正しいかを確認
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """これがコンセンサスアルゴリズム。すべてのネットワーク上のノードに対してチェーンをダウンロードし、ネットワーク上の最も長いチェーンで自らのチェーンを置き換えることでコンフリクトを解消する。
        :return: <bool> 自らのチェーンが置き換えられるとTrue, そうでなければFalse"""

        neighbours = self.nodes
        new_chain = None

        # 自らのチェーンより長いチェーンを探す必要がある
        max_length = len(selfl.chain)

        # 他のすべてのノードのチェーンを確認
        for node in neighbours:
            reponse = requests.get('http://{node}//chain'.format(node = node))

            if response.status_code == 200:
                length = reponse.json()['length']
                chain = reponse.json()['chain']

                # そのチェーンがより長いか、有効かを確認
                if length > max_length and self.valid_cahin(chian):
                    max_length = length
                    new_chain = chain

            # もし自らのチェーンより長く、かつ有効なチェーンを見つけた場合それを置き換える
            if new_chain:
                self.chain = new_chain
                return True

            return False

# ノードを作る
app = Flask(__name__)

# このノードにグローバルにユニークなアドレスを作る
node_identifire = str(uuid4()).replace('-', '')

# ブロックチェーンクラスをインスタンス化する
blockchain = Blockchain()

# メソッドはPOSTで/transactions/newエンドポイントを作る、POSTなのでデータを送信する
@app.route('/transactions/new', methods=['POST'])
def new_transactions():
    value = request.get_json()

    # POSTされたデータに必要なデータがあるかを確認
    required = ['sender', 'recipient', 'amount']
    if not all(k in value for k in required):
        return "Missing values", 400

    # 新しいトランザクションを作る
    index = blockchain.new_transactions(value['sender'], value['recipient'], value['amount'])

    return jsonify(response), 201

# メソッドはGETで/mineエンドポイントを作る
@app.route('/mine', methods=['GET'])
def mine():
    # 次のプルーフを見つけるためのプルーフ・オブ・ワークアルゴリズムを使用する
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # プルーフを見つけたことに対する報酬を得る
    # 送信者は、採掘者が新しいコインを採掘したことを表すために"0"とする
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifire,
        amount=1,
    )

    # チェーンに新しいブロックを加えることで、新しいブロックを採掘する
    block = blockchain.new_block(proof)

    response = {
        'message': '新しいブロックを採掘しました',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

# メソッドはGETで、フルのブロックチェーンをリターンする/chainエンドポイントを作る
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_node():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: 有効ではないノードのリストです, 400"

    for node in nodes:
        blockchain.register_node(node)

        response = {
            'message': '新しいノードが追加されました',
            'total_nodes':list(blockchain.nodes),
        }
        return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'チェーンが置き換えられました',
            'new_chain': blockchain.chain
        }
    else:
        reponse = {
            'message': 'チェーンが確認されました',
            'chain': blockchain.chain,
        }

    return jsonify(reponse), 200

# port5000でサーバーを起動する
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)