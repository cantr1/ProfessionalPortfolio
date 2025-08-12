# ==== APIs ====
import requests
import sys
import json
import os

from extra_funcs import pad_space, buffer

base_url = "https://pokeapi.co/api/v2/pokemon/"

class Pokemon:
    def __init__(self, name: str, data: dict) -> None:
        self.name = name
        self.data = self.create_poke_dict(data)

    def __str__(self) -> None:
        pad_space()
        print(f"Pokemon Name: {self.data['name']}")
        print(f"Pokemon ID: {self.data['id']}")
        print(f"Pokemon Type: {self.data['type']}")
        pad_space()
        print("Physical Characteristics: ")
        print(f"Height: {self.data['height_m']}m")
        print(f"Weight: {self.data['weight_kg']}kg")
        return (f"{self.name.title()} is ready to battle!")

    def create_poke_dict(self, data: dict) -> dict:
        """
        :param data: dict - data collected from the API
        :return: dict - structured info on the Pokémon
        """
        pokemon_info = {
            "name": data['name'].title(),
            "id": data['id'],
            "type": data['types'][0]['type']['name'].title(),
            "height_m": data['height'] / 10,
            "weight_kg": data['weight'] / 10,
            "hp": data['stats'][0]['base_stat']
        }

        return pokemon_info
    
    def get_pokemon_hp(self, data:dict) -> int:
        """
        :returns hp: int - hp of the given pokemon
        """
        hp = data.get('hp')
        return hp

    def print_pokemon_stats(self, data: dict) -> None:
        """
        :param data: dict - takes the collected data from the api as an input and returns the base stats of the pokemon
        """
        for stat in data["stats"]:
            base_stat: int = stat['base_stat']
            stat_name: str = stat["stat"]['name']
            print(f"{stat_name.upper()}: {base_stat}")
            setattr(self, stat_name, base_stat) #assign these variables to the object

    def get_pokemon_moves(self, data: dict) -> None:
        """
        :param data: dict - takes the collected data from the api as an input and returns the first four moves
        """
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
    def get_pokemon_info(poke_name: str) -> dict:
        """
        :return poke_data: dict - collects data from the api and returns it for other functions
        """
        full_url = base_url + poke_name
        response = requests.get(full_url)

        if response.status_code == 200:
            poke_data = response.json()
            return poke_data
        else:
            print(f"Faulty response: {response.json()}")
            sys.exit(1)

    @staticmethod
    def write_pokemon_data(poke_name: str) -> None:
        """
        :param poke_name: str - takes the name of the pokemon and writes the json file to the local dir
        """
        full_url = base_url + poke_name.lower()
        response = requests.get(full_url)

        file_path = os.path.join(os.getcwd(), "APIs", "Pokemon", "Data")

        if not os.path.exists(file_path):
            os.mkdir(file_path)

        with open(f"{file_path}/{poke_name}_data.json", "w") as f:
            json.dump(response.json(), f, indent=2) #optional indent for formatting