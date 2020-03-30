import json
from hashlib import sha256
import time
from flask import Flask, request
import requests
#import pymongo

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        """
        Constructor for the 'Block' class.
        :param index: Unique ID of the block.
        :param transactions: List of transactions.
        :param timestamp: Time of generation of the block.
        :param previous_hash: Hash of the previous block in the chain.
        """
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash

    def compute_hash(self):
        """
        Returns hash of the block instance by first converting it
        into JSON string.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest

class Blockchain:
    
    def __init__(self):
        
        self.unconfirmed_transactions = []
        self.chain = []#to do - load chain from disk. 
        #use mongodb for blockchain data.

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        #to do - create genesis block only if it does not exist
        genesis_block = Block(0, ["genesis_block : The Deemsys Genesis Block"], 0, "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
        db.transcripts.insert_one(self.chain[0])

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    @staticmethod
    def proof_of_authority(block):
        """
        Function that validates this entity can update the blockchain
        we need to add atleast one authenticator
        """
        pass

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)
        pass

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    
    def mine(self):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block

        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)

        proof = self.proof_of_authority(new_block)
        self.add_block(new_block, proof)

        self.unconfirmed_transactions = []

        return True

from pymongo import MongoClient

class Connect(object):
    @staticmethod    
    def get_connection():
        # mongo_uri will be in the project config file
        mongo_uri = "mongodb://localhost:27017/deemsys"  
        #return MongoClient("mongodb://$[username]:$[password]@$[hostlist]/$[database]?authSource=$[authSource]")
        return MongoClient(mongo_uri)


app = Flask(__name__)

# the node's copy of blockchain
blockchain = Blockchain()
#blockchain.create_genesis_block()
db = Connect.get_connection().get_default_database()
coll = db.get_collection('transcripts')
if coll.estimated_document_count() == 0:
    blockchain.create_genesis_block()
