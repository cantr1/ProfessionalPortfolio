from pokemon import Pokemon
from battle import battle_pokemon
from core import ask_user_continue, query
import os
    
def main() -> None:
    user_continue = True
    while user_continue:
        process = input("Would you like to battle pokemon or query the database? (b or q) ")

        if process.lower() == 'b':
            battle_pokemon()
        elif process.lower() == 'q':
            query()
        else:
            print("Invalid input...")

        if ask_user_continue():
            pass
        else:
            print("Bye!")
            user_continue = False

if __name__ == "__main__":
    os.system("clear")
    main()