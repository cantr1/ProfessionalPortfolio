from pokemon import Pokemon
import os
import sys

def get_pokemon_name() -> str:
    """
    :return pokemon_name: str - returns the name of the desired pokemon
    """
    pokemon_name: str = input("Enter Pokemon Name: ").lower()
    return pokemon_name

def ask_user_continue() -> bool:
    """
    :return: bool - returns if the user would like to continue
    """
    user_input = input("Would you like to query the database for another Pokemon? (y,n)").lower()
    if user_input == 'y':
        return True
    else:
        return False
    
def main() -> None:
    user_continue = True
    while user_continue:
        # name = get_pokemon_name()
        name = "pikachu" #set name for testing
        data = Pokemon.get_pokemon_info(name)
        pokemon = Pokemon(name, data)
        Pokemon.write_pokemon_data(name) #used to write json data to file

        if data:
            print(pokemon)
        else:
            print("Faulty response")
            sys.exit(1)

        pokemon.get_pokemon_moves(data)
        pokemon.print_pokemon_stats(data)

        battle = input("Would you like to battle these pokemon? y or n")
        if battle == 'y':
            pass #TODO: battle function

        if ask_user_continue():
            pass
        else:
            print("Bye!")
            user_continue = False

if __name__ == "__main__":
    os.system("clear")
    main()