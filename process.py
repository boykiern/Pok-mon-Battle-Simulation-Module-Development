from operator import itemgetter
import pandas as pd
from team import Team
from pokemon import Pokemon
from move import Move
from combat import __fight__, get_winner
import random
import csv


# File paths for output data
epochs_file_path = 'epochs.csv'
best_teams_file_path = 'mejores.csv'

# Create output CSVs and write headers
epochs_file = open(epochs_file_path, 'w', newline='')
best_teams_file = open(best_teams_file_path, 'w', newline='')
best_teams_file.write(
    'epoch,fitness,team_name,starter,pokemon_1,pokemon_2,pokemon_3,pokemon_4,pokemon_5,pokemon_6\n'
)

# Load input datasets
pokemon_data = pd.read_csv("pokemons.csv")
moves_data = pd.read_csv("moves.csv")

# Filter out legendary Pokémon
non_legendary_pokemon = pokemon_data[pokemon_data['is_legendary'] == 0]


def get_random_pokemon_list(count: int) -> list:
    """
    Select a random list of Pokémon (non-legendary) and return them as Pokemon objects.

    Args:
        count (int): Number of Pokémon to select.

    Returns:
        list: List of Pokemon objects ready to be used in teams.
    """
    selected = non_legendary_pokemon.sample(n=count, replace=False)
    pokemon_list = []

    for _, row in selected.iterrows():
        moves = []
        if row['moves'] == row['moves']:  # Check for NaN
            for m in row['moves'].split(";"):
                o = moves_data.loc[moves_data["name"] == m].iloc[0]
                moves.append(
                    Move(o["name"], o["type"], o["category"], o["pp"], o["power"], o["accuracy"])
                )
        if row['type2'] != row['type2']:  # Handle NaN in type2
            row['type2'] = ""

        poke = Pokemon(
            row['pokedex_number'], row['name'], row['type1'], row['type2'], row['hp'],
            row['attack'], row['defense'], row['sp_attack'], row['sp_defense'], row['speed'],
            row['generation'], row['height_m'], row['weight_kg'], row['is_legendary'], moves
        )
        pokemon_list.append(poke)

    return pokemon_list


def initialize_population(size: int, tag: str) -> list:
    """
    Create an initial population of teams.

    Args:
        size (int): Number of teams to generate.
        tag (str): Identifier for the generation (epoch).

    Returns:
        list: List of Team objects.
    """
    teams = []
    for i in range(size):
        pokemons = get_random_pokemon_list(6)
        team = Team(f"Team {i}-{tag}", pokemons)
        teams.append(team)
    return teams


def load_effectiveness_chart(filepath: str) -> dict:
    """
    Load type effectiveness chart into a dictionary.

    Args:
        filepath (str): Path to effectiveness_chart.csv.

    Returns:
        dict: Nested dictionary {attacking_type: {defending_type: multiplier}}.
    """
    with open(filepath, 'r') as file:
        lines = file.readlines()

    effectiveness = {}
    types = lines[0].strip().split(',')[1:]

    for line in lines[1:]:
        row = line.strip().split(',')
        attack_type = row[0]
        effectiveness[attack_type] = {}
        for idx, value in enumerate(row[1:]):
            defense_type = types[idx]
            effectiveness[attack_type][defense_type] = float(value)

    return effectiveness


def evaluate_fitness(opponents_count: int, teams: list, effectiveness: dict) -> tuple:
    """
    Evaluate the fitness of each team by simulating battles.

    Args:
        opponents_count (int): Number of opponents per team.
        teams (list): Teams to evaluate.
        effectiveness (dict): Type effectiveness chart.

    Returns:
        tuple: (Sorted list of best teams, list of (team_name, wins)).
    """
    wins_per_team = [[team.name, 0] for team in teams]
    opponents = initialize_population(opponents_count, "E")

    for idx, team in enumerate(teams):
        for opponent in opponents:
            result = get_winner(team, opponent, effectiveness)
            if result == team:
                wins_per_team[idx][1] += 1

    sorted_results = sorted(wins_per_team, key=itemgetter(1), reverse=True)

    best_teams = []
    for name, _ in sorted_results:
        for team in teams:
            if team.name == name:
                best_teams.append(team)
                break

    return best_teams, sorted_results


def crossover(teams: list, epoch: int) -> list:
    """
    Generate offspring teams by crossing over the best 20 teams.

    Args:
        teams (list): Parent teams.
        epoch (int): Current epoch number.

    Returns:
        list: List of offspring Team objects.
    """
    offspring = []
    for iteration in range(50):
        random_scores = [random.random() for _ in range(50)]
        for i in range(20):
            random_scores[i] *= 3

        team_indices = list(range(50))
        ranked = sorted(zip(team_indices, random_scores), key=lambda x: x[1], reverse=True)
        ranked_indices = [idx for idx, _ in ranked]

        pokes = []
        j = 0
        while j < 6:
            if random.random() >= 0.5:
                source = ranked_indices[0]
                candidate = teams[source].pokemons[j]
                if any(p.name == candidate.name for p in pokes):
                    source = ranked_indices[1]
                    candidate = teams[source].pokemons[j]
                pokes.append(candidate)
            else:
                source = ranked_indices[1]
                candidate = teams[source].pokemons[j]
                if any(p.name == candidate.name for p in pokes):
                    source = ranked_indices[0]
                    candidate = teams[source].pokemons[j]
                pokes.append(candidate)
            j += 1

        offspring.append(Team(f"Team {iteration}-{epoch}", pokes))

    return offspring


def mutation(teams: list):
    """
    Apply mutation with a 3% chance per Pokémon.

    Args:
        teams (list): List of Team objects.
    """
    for team in teams:
        for i, pokemon in enumerate(team.pokemons):
            if random.random() < 0.03:
                team.pokemons[i] = get_random_pokemon_list(1)[0]


def write_epochs_file(teams: list, epoch: int) -> None:
    """
    Write epoch data to epochs.csv.

    Args:
        teams (list): Teams in current epoch.
        epoch (int): Current epoch number.
    """
    counts = {}
    for team in teams:
        for poke in team.pokemons:
            counts[poke.name] = counts.get(poke.name, 0) + 1

    line = [str(epoch), str(len(counts))]
    sorted_counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))

    for name, qty in sorted_counts.items():
        line.append(f"{name}, {qty}")

    epochs_file.write(", ".join(line) + "\n")


def write_best_team(best_teams: list, fitness_list: list) -> None:
    """
    Write the best team of the epoch to mejores.csv.

    Args:
        best_teams (list): Sorted list of best teams.
        fitness_list (list): List of (team_name, fitness).
    """
    team = best_teams[0]
    parts = team.name.split('-')
    epoch = parts[1]

    line = [
        epoch,
        str(fitness_list[0][1]),
        str(fitness_list[0][0]),
        str(0)
    ] + [poke.name for poke in team.pokemons]

    best_teams_file.write(",".join(line) + "\n")


def run_evolution():
    """
    Run the evolutionary algorithm to optimize Pokémon teams.

    Returns:
        tuple: (Best team for battle, effectiveness dictionary).
    """
    initial_population = 50
    evaluation_opponents = 40
    teams = initialize_population(initial_population, "0")
    effectiveness = load_effectiveness_chart("effectiveness_chart.csv")
    epochs = 5

    for k in range(1, epochs + 1):
        print(f"Epoch {k}")
        teams, fitness_results = evaluate_fitness(evaluation_opponents, teams, effectiveness)
        write_best_team(teams, fitness_results)
        write_epochs_file(teams, k)

        if k < epochs:
            children = crossover(teams, k)
            mutation(children)
            teams = children

    battle_team = teams[0]
    epochs_file.close()
    best_teams_file.close()

    return battle_team, effectiveness


def main():
    run_evolution()


if __name__ == "__main__":
    main()
