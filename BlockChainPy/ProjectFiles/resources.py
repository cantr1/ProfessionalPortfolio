import os

# Directory where this script lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(BASE_DIR)
JSON_FILE = os.path.join(PARENT, "Data/blockchain.json")

banner = r"""
  ____                  _        ____        
 / ___|_ __ _   _ _ __ | |_ ___ |  _ \ _   _ 
| |   | '__| | | | '_ \| __/ _ \| |_) | | | |
| |___| |  | |_| | |_) | || (_) |  __/| |_| |
 \____|_|   \__, | .__/ \__\___/|_|    \__, |
            |___/|_|                   |___/ 
"""

prompt = "Choose one option: 🪙\n1.) View the blockchain\n2.) Create a new transaction\n3.) View last transaction\n4.) Exit\nChoice: "

welcome_message = r"""
  ====================================
   🔗 Welcome to Blockchain Emulator
  ====================================
     Initializing chain...
     Genesis block created.
     Ready to process transactions!
  """

exit_message = r"""
  ====================================
   🔗 Blockchain Emulator - Session Ended
  ====================================
     Thanks for testing the chain!
     Check the JSON for the full chain!
     Goodbye 👋
  """

transaction_message = r"""
  ====================================
   💸 Transaction Started
  ====================================
     Preparing block...
  """

chain_banner = r"""
  ====================================
   ⛓️  Current Blockchain State
  ====================================
     Displaying all blocks...
  """

last_transaction_message = r"""
  ====================================
   📝 Last Transaction in Block
  ====================================
     Retrieving latest entry...
  """