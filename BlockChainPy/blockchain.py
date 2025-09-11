from time import time
from uuid import uuid4
import hashlib
import json

class Blockchain():
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        #Create the genesis block
        self.new_block(index=0, previous_hash=1, proof=100)

    def new_block(self, index: int, previous_hash: int, proof: int):
        """
        Creates a new block and adds it to the chain.
        """
        # Index value will increment by one, using the len function to get the value needed
        block = {
            'index': index,
            'timestamp': time(),
            'transaction': self.current_transactions,
            'proof': proof,
            'hash': None, # Set temp
            'previous_hash': previous_hash,}
        
        # Create a hash of the block - not perfect system, but fine for this project
        block['hash'] = self.hash(block)

        # Write to the chain
        self.chain.append(block)

        # Reset current transactions
        self.current_transactions = []

        return block
        

    def new_transaction(self, sender: str, recipient: str, amount: int) -> None:
        """
        Creates a new transaction, logs it in current transactions
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        )

    def proof_of_work(self, last_proof: int) -> int:
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        :param last_proof: - int
        :return: -int
        """

        proof = 0

        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof:int, proof: int) -> int:
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: int - Previous Proof
        :param proof: int - Current Proof
        :return: bool - True if correct, False if not.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @staticmethod
    def hash(block: dict):
        """
        :param block: str - block to hash
        :returns hash_block: str - hashed block
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """
        :returns last_block: str - last block in the chain
        """
        return self.chain[len(self.chain) - 1]
    