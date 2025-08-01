# ==== APIs ====
import requests
import sys
import json

base_url = "https://pokeapi.co/api/v2/pokemon/"

class Pokemon:
    def __init__(self, name: str) -> None:
        self.name = name

    def get_pokemon_info(self) -> dict:
        full_url = base_url + self.name
        response = requests.get(full_url)

        if response.status_code == 200:
            poke_data = response.json()
            return poke_data
        else:
            print(f"Faulty response: {response.json()}")
            sys.exit(1)

    def print_pokemon_info(self, data) -> None:
        print(f"Pokemon information for {self.name.title()}")
        print(f"Pokemon Name: {data['name'].title()}")
        print(f"Pokemon ID: {data['id']}")

    def get_pokemon_moves(self, data: dict) -> None:
        print(f"{self.name.title()}'s available moves:")
        for ability in data["abilities"]:
            print(ability['ability']['name'].title())

def get_pokemon_name() -> str:
    pokemon_name: str = input("Enter Pokemon Name: ").lower()
    return pokemon_name

def main() -> None:
    # name = get_pokemon_name()
    name = "pikachu"
    pokemon = Pokemon(name)
    data = pokemon.get_pokemon_info()

    if data:
        pokemon.print_pokemon_info(data)
    else:
        print("Faulty response")
        sys.exit(1)

    pokemon.get_pokemon_moves(data)

if __name__ == "__main__":
    main()
