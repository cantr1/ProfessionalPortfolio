from blockchain import Blockchain
from mqtt.publisher import publish_blockchain
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
    successful_publish,
    failed_publish,
    JSON_FILE
)

def write_to_file(data: Blockchain) -> None:
    with open(JSON_FILE, "w") as file:
        json.dump(data, file, indent=4)

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
    while True:
        try:
            usr_choice = int(input(prompt))
            return usr_choice
        except ValueError:
            print("❌ Please use a valid integer...")

def view_chain(blockchain: Blockchain) -> None:
    # Pretty print
    try:
        print(json.dumps(blockchain.chain, indent=4))
    except:
        print(json.dumps(blockchain, indent=4))

def main() -> None:
    try:
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

                # Build the block and append to current transactions
                blockchain.new_transaction(sender, recipient, amount)

                # Write it to the chain 
                block = blockchain.new_block(len(blockchain.chain), 
                                     blockchain.last_block['hash'], 
                                     blockchain.proof_of_work(blockchain.last_block['proof']))

                # Publish to MQTT Container
                try:
                    publish_blockchain(block)
                    print(successful_publish)
                except ConnectionRefusedError:
                    print(failed_publish)

            
            elif usr_choice == 3:
                clear_screen()
                print(last_transaction_message)
                view_chain(blockchain.last_block)

            elif usr_choice == 4:
                print(exit_message)
                write_to_file(blockchain.chain)
                sys.exit(0)

            else:
                print("❌ ERROR: Unrecognized input...")
    except KeyboardInterrupt:
        print("Interrupt detected...")
        print(exit_message)

if __name__ == "__main__":
    main()

