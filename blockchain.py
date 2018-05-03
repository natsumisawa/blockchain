import hashlib
import json
from time import time
from uuid import uuid4

class Blockchain(object):
    def __init__(self):
        # ブロックチェーンを収めるための空リスト
        self.chain = []
        # トランザクションを収めるための空リスト
        self.current_transactions = []

        # ジェネシスブロックを作る
        self.new_block(previous_hash=1, proof=100)

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

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigests()

        return guess_hash[:4] == "0000"