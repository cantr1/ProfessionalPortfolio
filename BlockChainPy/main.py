from blockchain import Blockchain
import sys
import os
import json
from resources import (
    banner,
    prompt,
    welcome_message,
    exit_message,
    transaction_message,
    chain_banner,
    last_transaction_message,
)

def clear_screen() -> None:
    """
    Clears terminal screen when called
    """
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For macOS, Linux, and other Unix-like systems
        os.system('clear')

def prompt_user() -> int:
    """
    :returns usr_choice: int
    Displays prompt and asks user to choose an option
    """
    usr_choice = int(input(prompt))

    return usr_choice

def view_chain(blockchain: Blockchain) -> None:
    # Pretty print
    try:
        print(json.dumps(blockchain.chain, indent=4))
    except:
        print(json.dumps(blockchain, indent=4))

def main() -> None:
    # Initialize a blockchain
    blockchain = Blockchain()

    # Clear terminal screen
    clear_screen()

    print(banner)
    print(welcome_message)

    # Prompt the user for input and create an infinite while loop
    while True:
        usr_choice = prompt_user()

        if usr_choice == 1:
            clear_screen()
            print(chain_banner)
            view_chain(blockchain)
            print("\n")

        elif usr_choice == 2:
            clear_screen()
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
            clear_screen()
            print(last_transaction_message)
            view_chain(blockchain.last_block)

        elif usr_choice == 4:
            print(exit_message)
            sys.exit(0)

        else:
            print("❌ ERROR: Unrecognized input...")

if __name__ == "__main__":
    main()

