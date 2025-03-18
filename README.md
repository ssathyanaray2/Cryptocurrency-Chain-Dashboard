# Cryptocurrency Blockchain

# Overview
This is a simple blockchain-based cryptocurrency implementation using Python and Flask. It supports basic blockchain operations such as transaction management, mining, and network node communication.

## Features
- Generates RSA key pairs for transactions
- Implements proof-of-work mining with adjustable difficulty
- Allows adding and validating transactions
- Maintains a decentralized blockchain with multiple nodes
- Supports balance checking and transaction history

## Requirements
Make sure you have Python installed and install the required dependencies:

pip install requirements.txt

## Steps to Run
1. Navigate to the project folder and run the following command:

python node5001.py

2. The blockchain will start running on `http://0.0.0.0:5001`.

## API Endpoints

1. Mine a Block
- GET /mine_block
- Mines a new block if there are valid transactions.

2. Get the Blockchain
- GET /get_chain
- Retrieves the full blockchain.

3. Check Blockchain Validity
- GET /is_valid
- Verifies if the blockchain is valid.

4. Add a Transaction
- POST /add_transaction
- Adds a new transaction to the pending transaction list.
  json
  {
    "receiver": "<receiver_public_key>",
    "amount": <amount>
  }
  
5. Connect Nodes
- POST /connect_node
- Connects a new node to the blockchain network.
  {
    "nodes": ["http://127.0.0.1:5002"]
  }

6. Replace the Chain
- GET /replace_chain
- Replaces the chain with the longest valid chain in the network.

7. View Pending Transactions(Yet to be mined)
- GET /show_transactions
- Displays pending transactions.

8. Check Account Balance
- GET /calculate_balance
- Retrieves the balance of the current node's wallet.

9. Get Public Key
- GET /show_publickey
- Retrieves the public key of the node.

## Running Multiple Nodes
To simulate a network with multiple nodes:
- Change the port number in app.run() (e.g., `5002`, `5003`) and run the script multiple times.
- Use /connect_node to link the nodes.
