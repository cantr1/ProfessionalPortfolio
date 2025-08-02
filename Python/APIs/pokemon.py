# ==== APIs ====
import requests
import sys
import json
import os

from extra_funcs import pad_space, buffer

base_url = "https://pokeapi.co/api/v2/pokemon/"

class Pokemon:
    def __init__(self, name: str) -> None:
        self.name = name

    def get_pokemon_info(self) -> dict:
        """
        :return poke_data: dict - collects data from the api and returns it for other functions
        """
        full_url = base_url + self.name
        response = requests.get(full_url)

        if response.status_code == 200:
            poke_data = response.json()
            return poke_data
        else:
            print(f"Faulty response: {response.json()}")
            sys.exit(1)

    def print_pokemon_info(self, data: dict) -> None:
        """
        :param data: dict - takes the collected data from the api as an input and information on the pokemon
        """
        pad_space()
        print(f"Pokemon Name: {data['name'].title()}")
        print(f"Pokemon ID: {data['id']}")
        print(f"Pokemon Type: {data['types'][0]['type']['name'].title()}")
        buffer()
        print("Physical Characteristics: ")
        print(f"Height: {data['height'] / 10}m")
        print(f"Weight: {data['weight'] / 10}kg")

    def print_pokemon_stats(self, data: dict) -> None:
        """
        :param data: dict - takes the collected data from the api as an input and returns the base stats of the pokemon
        """
        pad_space()
        for stat in data["stats"]:
            base_stat: int = stat['base_stat']
            stat_name: str = stat["stat"]['name']
            print(f"{stat_name.upper()}: {base_stat}")

    def get_pokemon_moves(self, data: dict) -> None:
        """
        :param data: dict - takes the collected data from the api as an input and returns the first four moves
        """
        pad_space()
        print(f"{self.name.title()}'s available starter moves:")
        x = 0
        while x < 4: # Creating while loop to display only four moves
            for move in data["moves"]:
                    if x == 4:
                        break
                    if move["version_group_details"][0]["level_learned_at"] == 0:
                        print(move['move']['name'].title())
                        x += 1

    @staticmethod
    def write_pokemon_data(poke_name: str) -> None:
        """
        :param poke_name: str - takes the name of the pokemon and writes the json file to the local dir
        """
        full_url = base_url + poke_name.lower()
        response = requests.get(full_url)

        with open(f"/Users/kelz/Documents/Python/APIs/{poke_name}_data.json", "w") as f:
            json.dump(response.json(), f, indent=2) #optional indent for formatting


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
        name = get_pokemon_name()
        # name = "pikachu" #set name for testing
        pokemon = Pokemon(name)
        data = pokemon.get_pokemon_info()
        Pokemon.write_pokemon_data(name) #used to write json data to file

        if data:
            pokemon.print_pokemon_info(data)
        else:
            print("Faulty response")
            sys.exit(1)

        pokemon.get_pokemon_moves(data)
        pokemon.print_pokemon_stats(data)

        if ask_user_continue():
            pass
        else:
            print("Bye!")
            user_continue = False

if __name__ == "__main__":
    os.system("clear")
    main()
