import datetime
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature.pkcs1_15 import PKCS115_SigScheme
from Cryptodome.Hash import SHA256
from base64 import b64encode, b64decode
from flask_cors import CORS

class Blockchain:
    def rsakeys(self):  
         privatekey = RSA.generate(2048)
         publickey = privatekey.publickey().exportKey()
         return privatekey, publickey
     
    def __init__(self):
        self.chain=[]
        self.transactions=[]
        self.difficulty=4
        self.hash_pattern='0'
        self.balancecurrency=100
        self.nodes=set()
        keys=self.rsakeys()
        self.privatekey=keys[0]
        self.publickey=keys[1]
        genesis=self.contents_block(previous_hash='0')
        self.proof_of_work(genesis)
        self.create_block(genesis)
 
    def sign(self, privatekey, data):
        signer = PKCS115_SigScheme(privatekey)
        signature=signer.sign(data)
        return b64encode(signature).decode('ASCII')
    
    def verify(self, publickey, data,sign):
        pubbytes = b64decode(publickey)
        pk = RSA.import_key(pubbytes)
        signature = b64decode(sign)
        try:
            verifier = PKCS115_SigScheme(pk)
            verifier.verify(data, signature)
            return True
        except:
            return False
        
    def contents_block(self,previous_hash):
        for i in self.transactions:
            i['trans_hash']=i['trans_hash'].hexdigest()
        block_contents={'index':len(self.chain)+1,
               'timestamp':str(datetime.datetime.now()),
               'previous_hash':previous_hash,
               'transactions':self.transactions
               }
        self.transactions=[]
        network = self.nodes
        for node in network:
            url = 'http://'+str(node)+'/update_trans_list'
            param = {'key':None}
            requests.post(url, json = param)
        return block_contents
    
    def create_block(self,block_contents):
        self.chain.append(block_contents)
        return block_contents
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, blockcontents):
        hash_operation=None
        blockcontents['proof']=1
        check_proof=False
        while(check_proof is False):
            hash_operation=self.hash(blockcontents)
            if hash_operation[:self.difficulty]==self.hash_pattern*self.difficulty:
                check_proof=True
            else:
                blockcontents['proof']+=1   
    
    def hash(self, block):
        encoded_block=json.dumps(block, sort_keys=True).encode()
        return SHA256.new(encoded_block).hexdigest()
    
    def transhash(self,block):
        encoded_block=json.dumps(block, sort_keys=True).encode()
        return SHA256.new(encoded_block)
    
    def is_chain_valid(self, chain):
        previous_block=chain[0]
        block_index=1
        while block_index<len(chain):
            block=chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            hash_operation=self.hash(block)
            if hash_operation[:self.difficulty] !=self.hash_pattern*self.difficulty:
                return False
            previous_block=block
            block_index+=1
        return True
    
    def add_transactions(self, receiver, amount):
        balanceamount=self.balance()
        if balanceamount<amount:
            return False
        sender=b64encode(self.publickey).decode('ASCII')    
        trans={'sender':sender, 'receiver':receiver, 'amount':amount}
        trans['timestamp']=str(datetime.datetime.now())
        transtemp=trans.copy()
        trans_hash=self.transhash(transtemp)
        trans['trans_hash']=trans_hash
        signature=self.sign(self.privatekey,trans_hash)
        trans['signature']=signature
        transtemp['signature']=signature
        self.transactions.append(trans)
        network = self.nodes
        for node in network:
            url = 'http://'+str(node)+'/update_trans_list'
            param = {'trans':transtemp}
            requests.post(url, json = param)
        return True
            
    def add_transaction(self, trans):
        transtemp=trans.copy()
        transtemp.pop('signature')
        trans['trans_hash']=self.transhash(transtemp)
        self.transactions.append(trans)
    
    def add_node(self, address):
        parsed_url=urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False     
    
    def has_valid_transactions(self):
        invalid_trans=[]
        j=0
        for i in self.transactions:
            trans={'sender':i['sender'], 'receiver':i['receiver'], 'amount':i['amount'], 'timestamp':i['timestamp']}
            #print(type(i['trans_hash']))
            #print(type(self.transhash(trans)))
            generate_hash=self.transhash(trans)
            verified=self.verify(i['sender'],generate_hash, i['signature'])
            if not verified or i['amount']>self.balance(i['sender']) or i['trans_hash'].hexdigest() != generate_hash.hexdigest():
                invalid_trans.append(j)
            j+=1
        if len(invalid_trans)==len(self.transactions):
            return False
        for i in invalid_trans:
            self.transactions.pop(i)
        return True
    
    def showpending_transactions(self):
        return self.transactions
        
        
    def balance(self, publickey=""):
        balanceamt=100
        if publickey == "":
            publickey=b64encode(self.publickey).decode('ASCII')
        for block in self.chain:
            trans=block['transactions']
            for transaction in trans:
                if transaction['sender']==publickey:
                    balanceamt= balanceamt-transaction['amount']
                elif transaction['receiver']==publickey:
                    balanceamt= balanceamt+transaction['amount']
        self.balancecurrency=balanceamt
        return self.balancecurrency
        
    
#flask application   
app=Flask(__name__)

CORS(app)

node_address=str(uuid4()).replace('-','')

blockchain=Blockchain()

@app.route('/mine_block', methods=['GET'])
def mine_block():
    if not blockchain.has_valid_transactions():
        return jsonify({'message':'No valid transactions to mine'}), 400
    reward={'sender':node_address,
                'receiver':b64encode(blockchain.publickey).decode('ASCII'),
                'amount':1,
                'timestamp':str(datetime.datetime.now())}
    reward['trans_hash']=blockchain.transhash(reward)
    blockchain.transactions.append(reward)
    previous_block=blockchain.get_previous_block()
    previous_hash=blockchain.hash(previous_block)
    contentsofblock=blockchain.contents_block(previous_hash)
    blockchain.proof_of_work(contentsofblock)
    block=blockchain.create_block(contentsofblock)
    response={'message':'Congratulations, you just mined a block',
              'index':block['index'],
              'timestamp':block['timestamp'],
              'proof':block['proof'],
              'previous_hash':block['previous_hash'],
              'transactions':block['transactions']}
    return jsonify(response), 200

@app.route('/get_chain', methods=['GET'])
def get_chain():
    response={'chain':blockchain.chain,
              'length':len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid', methods=['GET'])
def is_valid():
    if blockchain.is_chain_valid(blockchain.chain):
        response={'message':'The Blockchain is valid'}
    else:
        response={'message':'The Blockchain is not valid'}
    return jsonify(response), 200

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json=request.get_json()
    transaction_keys=['receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    success=blockchain.add_transactions(json['receiver'],json['amount'])
    if success==True:
        response={'message':'This transaction will be added to block',}
    else:
        response={'message':'Your balance is less than the amount!!',}
    return jsonify(response), 201
    
@app.route('/connect_node', methods=['POST'])
def connect_node():
    json=request.get_json()
    nodes=json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response={'message':'All the nodes are connected. The nodes in the blockchain are :',
              'total_nodes':list(blockchain.nodes)}
    return jsonify(response), 201

@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response={'message':'The chain was replaced by the largest chain',
                  'new_chain':blockchain.chain}
    else:
        response={'message':'No change. The chain is the largest one',
                  'actual_chain':blockchain.chain}
    return jsonify(response), 200

@app.route('/update_trans_list', methods=['POST'])
def update_trans_list():
    json=request.get_json()
    if 'key' in json and json['key']==None:
        blockchain.transactions.clear()
        return 'All transactions removed', 200
    if 'trans' not in json:
        return 'Some elements of the transaction are missing', 400
    blockchain.add_transaction(json['trans'])
    response={'message':'This transaction will be added to block'}
    return jsonify(response), 201

@app.route('/show_transactions', methods=['GET'])
def show_transactions():
    pending_transactions = blockchain.showpending_transactions()
    if len(pending_transactions)==0:
        response={'message':'There are no pending transactions',
                  'pending_transactions':pending_transactions}
        return response
    else:
        filtered_transactions = [
        {
            "sender": transaction["sender"],
            "receiver": transaction["receiver"],
            "amount": transaction["amount"]
        }
        for transaction in pending_transactions
        ]

        print(filtered_transactions)
        return jsonify({'pending_transactions': filtered_transactions}), 200


@app.route('/calculate_balance', methods=['GET'])
def calculate_balance():
    get_balance=blockchain.balance()
    response={'balance':get_balance,}
    return jsonify(response), 200
    
    
@app.route('/show_publickey', methods=['GET'])
def show_publickey():
    publickey=b64encode(blockchain.publickey).decode('ASCII')
    response={'publickey':publickey,}
    return jsonify(response), 200
    
    
app.run(host='0.0.0.0', port=5001)
