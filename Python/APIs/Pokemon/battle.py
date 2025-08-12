from core import get_pokemon_name
from pokemon import Pokemon
import os
import time

def display_hp(pk1: Pokemon, pk1_hp: int, pk2: Pokemon, pk2_hp: int) -> None:
    print(f"{pk1.name.title()} === {pk2.name.title()}")
    print(f"HP: {pk1_hp} ===== {pk2_hp}")

def deal_damage(dmg: int, target: Pokemon, hp:int) -> int:
    print("The attack is effective!")
    print(f"{target.name.title()} takes {dmg} damage!")
    return hp - dmg

def create_pokemon() -> Pokemon:
    """
    :returns pokemon: Pokemon - creates a Pokemon object
    """
    pokemon_name = get_pokemon_name()
    pk_data = Pokemon.get_pokemon_info(pokemon_name)
    pokemon = Pokemon(pokemon_name, pk_data)
    print(f'Pokemon Ready to battle: {pokemon.name.title()}!')
    return pokemon

def battle_pokemon() -> None:
    pokemon_1 = create_pokemon()
    pk1_data = pokemon_1.get_pokemon_info(pokemon_1.name)
    pk1_dict = pokemon_1.create_poke_dict(pk1_data)
    pk1_hp = pokemon_1.get_pokemon_hp(pk1_dict)

    pokemon_2 = create_pokemon()
    pk2_data = pokemon_2.get_pokemon_info(pokemon_2.name)
    pk2_dict = pokemon_2.create_poke_dict(pk2_data)
    pk2_hp = pokemon_2.get_pokemon_hp(pk2_dict)

    turn = 1 # track which pokemon's turn it is
    while pk1_hp > 0 and pk2_hp > 0:
        display_hp(pokemon_1, pk1_hp, pokemon_2, pk2_hp)

        if turn == 1:
            print(f"It's {pokemon_1.name.title()}'s turn!")
            pokemon_1.get_pokemon_moves(pk1_data)
            input("Choose a move!")
            pk2_hp = deal_damage(10, pokemon_2, pk2_hp)
            turn = 2
        elif turn == 2:
            print(f"It's {pokemon_2.name.title()}'s turn!")
            pokemon_2.get_pokemon_moves(pk2_data)
            input("Choose a move! ")
            pk1_hp = deal_damage(10, pokemon_1, pk1_hp)
            turn = 1

        time.sleep(2)
        os.system('clear')

if __name__ == '__main__':
    print("Called as main... Run Main file to battle")