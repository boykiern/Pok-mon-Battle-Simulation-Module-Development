import pandas as pd
from team import Team
from pokemon import Pokemon
from move import Move
from combat import __faint_change__, get_winner
from proceso import obtener_equipo


def build_koga_team():
    """
    Builds Koga's Pokémon team (6 Pokémon) using data from pokemons.csv and moves.csv.

    Returns:
        Team: A Team object with Koga's Pokémon ready for battle.
    """
    pokemon_data = pd.read_csv("pokemons.csv")
    moves_data = pd.read_csv("moves.csv")

    koga_pokemons = ['Skunktank', 'Toxicroak', 'Swalot', 'Venomoth', 'Muk', 'Crobat']

    # Select only Koga's Pokémon
    koga_team_df = pokemon_data[pokemon_data['name'].isin(koga_pokemons)]

    pokemons_list = []
    for _, row in koga_team_df.iterrows():
        moves = []
        if not pd.isna(row['moves']):
            for move_name in row['moves'].split(";"):
                move_row = moves_data.loc[moves_data["name"] == move_name].iloc[0]
                moves.append(
                    Move(
                        move_row["name"],
                        move_row["type"],
                        move_row["category"],
                        move_row["pp"],
                        move_row["power"],
                        move_row["accuracy"]
                    )
                )

        pokemon_obj = Pokemon(
            row['pokedex_number'],
            row['name'],
            row['type1'],
            None if pd.isna(row['type2']) else row['type2'],
            row['hp'],
            row['attack'],
            row['defense'],
            row['sp_attack'],
            row['sp_defense'],
            row['speed'],
            row['generation'],
            row['height_m'],
            row['weight_kg'],
            row['is_legendary'],
            moves
        )
        pokemons_list.append(pokemon_obj)

    return Team("Koga Team", pokemons_list, 0)


def is_team_defeated(team: Team) -> bool:
    """Check if all Pokémon in a team have fainted."""
    return all(pokemon.current_hp <= 0 for pokemon in team.pokemons)


def get_next_active_pokemon(team: Team):
    """Return the next non-fainted Pokémon from the team."""
    for pokemon in team.pokemons:
        if pokemon.current_hp > 0:
            return pokemon
    return None


def battle(team1: Team, team2: Team, effectiveness: dict):
    """
    Simulates a battle between two Pokémon teams.

    Args:
        team1 (Team): The first team of 6 Pokémon.
        team2 (Team): The second team of 6 Pokémon.
        effectiveness (dict): Dictionary with type effectiveness multipliers.

    Returns:
        None
    """
    turn = 0
    print(f"{team1.name} vs {team2.name}")

    while any(p.current_hp > 0 for p in team1.pokemons) and any(p.current_hp > 0 for p in team2.pokemons):
        print(f"Turn {turn + 1}:")
        team1_pokemon = team1.get_current_pokemon()
        team2_pokemon = team2.get_current_pokemon()

        print(f"{team1.name}'s {team1_pokemon.name} vs {team2.name}'s {team2_pokemon.name}\n")

        # Handle fainted Pokémon
        if team1_pokemon.current_hp <= 0 or team2_pokemon.current_hp <= 0:
            __faint_change__(team1, team2, effectiveness)
            print(f"{team1.name} fainted count: {sum(p.current_hp <= 0 for p in team1.pokemons)}")
            print(f"{team2.name} fainted count: {sum(p.current_hp <= 0 for p in team2.pokemons)}\n")
            continue

        # Get next actions
        action1, target1 = team1.get_next_action(team2, effectiveness)
        action2, target2 = team2.get_next_action(team1, effectiveness)

        # Team 1 action
        if action1 == 'switch':
            print(f"{team1.name} switches {team1_pokemon.name}\n")
            team1.do_action(action1, target1, team2, effectiveness)
        elif action1 == 'attack':
            move, damage = team1_pokemon.get_best_attack(team2_pokemon, effectiveness)
            print(f"{team1.name}'s {team1_pokemon.name} uses {move.name}, dealing {damage} damage\n")
            team2_pokemon.current_hp -= damage

        # Team 2 action
        if action2 == 'switch':
            print(f"{team2.name} switches {team2_pokemon.name}\n")
            team2.do_action(action2, target2, team1, effectiveness)
        elif action2 == 'attack':
            move, damage = team2_pokemon.get_best_attack(team1_pokemon, effectiveness)
            print(f"{team2.name}'s {team2_pokemon.name} uses {move.name}, dealing {damage} damage\n")
            team1_pokemon.current_hp -= damage

        # Print current HP
        print(f"{team1_pokemon.name} HP: {team1_pokemon.current_hp}\n")
        print(f"{team2_pokemon.name} HP: {team2_pokemon.current_hp}\n")

        # Handle faint after damage
        if team1_pokemon.current_hp <= 0 or team2_pokemon.current_hp <= 0:
            __faint_change__(team1, team2, effectiveness)
            print(f"{team1.name} fainted count: {sum(p.current_hp <= 0 for p in team1.pokemons)}")
            print(f"{team2.name} fainted count: {sum(p.current_hp <= 0 for p in team2.pokemons)}\n")

        turn += 1

    # Determine winner
    winner = get_winner(team1, team2, effectiveness)
    print(f"The winner is {winner.name}")


def main():
    koga_team = build_koga_team()
    optimized_team, effectiveness_dict = obtener_equipo()
    # Run the battle
    battle(optimized_team, koga_team, effectiveness_dict)


if __name__ == "__main__":
    main()
