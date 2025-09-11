from blockchain import Blockchain
from resources import banner, prompt, welcome_message, exit_message, transaction_message, chain_banner
import sys
import json

def prompt_user() -> int:
    """
    :returns usr_choice: int
    Displays prompt and asks user to choose an option
    """
    usr_choice = int(input(prompt))

    return usr_choice

def view_chain(blockchain: Blockchain) -> None:
    # Pretty print
    print(json.dumps(blockchain.chain, indent=4))

def main() -> None:
    # Initialize a blockchain
    blockchain = Blockchain()

    print(banner)
    print(welcome_message)

    # Prompt the user for input and create an infinite while loop
    while True:
        usr_choice = prompt_user()

        if usr_choice == 1:
            print(chain_banner)
            view_chain(blockchain)
            print("\n")

        elif usr_choice == 2:
            print(transaction_message)
            sender = input("🐳 Who is the sender: ")
            recipient = input("🤑 Who is the recipient: ")
            amount = input("💰 What is the transaction amount: ")

            # Build the block
            blockchain.new_transaction(sender, recipient, amount)

            # Write it to the chain 
            # TODO: Implement proof feature
            blockchain.new_block(len(blockchain.chain), blockchain.last_block['hash'], 0)
            print("\n")

        elif usr_choice == 3:
            print(exit_message)
            sys.exit(0)

if __name__ == "__main__":
    main()

