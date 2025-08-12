from pokemon import Pokemon
import sys
from extra_funcs import pad_space

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
    user_input = input("Would you like to continue? (y,n) ").lower()
    if user_input == 'y':
        return True
    else:
        return False

def query() -> None:
    name = get_pokemon_name()
    #name = "pikachu" #set name for testing
    data = Pokemon.get_pokemon_info(name)
    pokemon = Pokemon(name, data)
    Pokemon.write_pokemon_data(name) #used to write json data to file

    if data:
        print(pokemon)
    else:
        print("Faulty response")
        sys.exit(1)

    pad_space()
    pokemon.get_pokemon_moves(data)
    pad_space()
    pokemon.print_pokemon_stats(data)
    pad_space()