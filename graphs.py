import pandas as pd
import csv
import matplotlib.pyplot as plt
from math import pi


def build_radar_dict(best_teams_file, pokemons_file):
    """
    Build a dictionary of Pokémon stats for the best team found by the algorithm.

    Args:
        best_teams_file (file): File object containing the best teams (CSV).
        pokemons_file (file): File object containing Pokémon data (CSV).

    Returns:
        dict: Dictionary mapping Pokémon names to their stats 
              [Attack, Defense, HP, Speed, Sp. Defense, Sp. Attack].
    """
    lines = best_teams_file.readlines()
    last_line = lines[-1].strip()
    pokemon_names = last_line.split(',')[4:]  # Pokémon names start from 5th column

    pokemon_stats = {}

    reader = csv.DictReader(pokemons_file)
    for row in reader:
        name = row['name']
        if name in pokemon_names:
            attack = int(row['attack'])
            defense = int(row['defense'])
            hp = int(row['hp'])
            speed = int(row['speed'])
            sp_defense = int(row['sp_defense'])
            sp_attack = int(row['sp_attack'])

            pokemon_stats[name] = [attack, defense, hp, speed, sp_defense, sp_attack]

    return pokemon_stats


def radar_chart(best_team_stats: dict):
    """
    Generate a radar chart showing stats of the best team found.

    Args:
        best_team_stats (dict): Dictionary with Pokémon names as keys and their stats as values.
    """
    categories = ['Attack', 'Defense', 'HP', 'Speed', 'Sp. Defense', 'Sp. Attack']
    num_vars = len(categories)

    # Compute angles for each axis
    angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
    angles += angles[:1]

    # Initialize figure
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    # Plot each Pokémon
    for pokemon, values in best_team_stats.items():
        values += values[:1]
        ax.plot(angles, values, label=pokemon)
        ax.fill(angles, values, alpha=0.25)

    # Labels
    plt.xticks(angles[:-1], categories)
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.title('Best Team Stats')
    plt.show()


def plot_fitness_evolution():
    """
    Plot the fitness of the best team across generations (epochs).
    """
    df = pd.read_csv('mejores.csv')
    fitness = df['aptitud']
    epochs = range(1, len(df) + 1)

    plt.figure(figsize=(10, 6))
    plt.plot(epochs, fitness, marker='o', linestyle='-', color='b', label='Fitness')
    plt.xlabel('Epoch')
    plt.ylabel('Fitness')
    plt.title('Best Team Fitness Over Generations')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def bar_chart(epochs_file):
    """
    Plot a horizontal bar chart showing Pokémon frequencies in the last recorded epoch.

    Args:
        epochs_file (file): File object with epoch data.
    """
    last_line = list(epochs_file)[-1].strip()
    data = last_line.split(', ')

    pokemon_names = []
    quantities = []

    for i in range(2, len(data), 2):
        name = data[i]
        count = int(data[i + 1])
        pokemon_names.append(name)
        quantities.append(count)

    # Sort by frequency (descending)
    stats = list(zip(pokemon_names, quantities))
    stats.sort(key=lambda x: x[1], reverse=True)

    sorted_names = [x[0] for x in stats]
    sorted_counts = [x[1] for x in stats]

    plt.figure(figsize=(12, 6))
    plt.barh(sorted_names, sorted_counts, color='skyblue')
    plt.xlabel('Count')
    plt.ylabel('Pokémon')
    plt.title('Pokémon Frequency in Last Epoch')
    plt.gca().invert_yaxis()
    plt.show()


def process_pokemon_data(epochs_file, pokemons_file):
    """
    Process epoch and Pokémon data to count types in the last epoch.

    Args:
        epochs_file (file): File object with epoch data.
        pokemons_file (file): File object with Pokémon stats.

    Returns:
        dict: Dictionary where keys are Pokémon types and values are counts.
    """
    epochs_file.seek(0)
    lines = epochs_file.readlines()
    last_line = lines[-1].strip()

    elements = last_line.split(', ')
    names = elements[2::2]
    quantities = elements[3::2]

    type_counts = {}

    pokemons_file.seek(0)
    reader = csv.DictReader(pokemons_file)

    for row in reader:
        if row['name'] in names:
            count = int(quantities[names.index(row['name'])])
            types = [row['type1']]
            if row['type2']:
                types.append(row['type2'])
            for t in types:
                type_counts[t] = type_counts.get(t, 0) + count

    return type_counts


def plot_type_distribution(type_dict: dict):
    """
    Plot the type distribution of the Pokémon team from the last epoch.

    Args:
        type_dict (dict): Dictionary with Pokémon types and counts.
    """
    types = list(map(str, type_dict.keys()))
    counts = list(type_dict.values())

    plt.figure(figsize=(10, 6))
    plt.bar(types, counts, color='skyblue')
    plt.xlabel('Pokémon Types')
    plt.ylabel('Count')
    plt.title('Pokémon Type Distribution in Last Epoch')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def main():
    epochs_file_path = 'epochs.csv'
    best_teams_file_path = 'mejores.csv'
    pokemons_file_path = 'pokemons.csv'

    epochs_file = open(epochs_file_path, 'r')
    best_teams_file = open(best_teams_file_path, 'r')
    pokemons_file = open(pokemons_file_path, 'r')

    radar_dict = build_radar_dict(best_teams_file, pokemons_file)
    radar_chart(radar_dict)
    bar_chart(epochs_file)
    plot_fitness_evolution()
    type_counts = process_pokemon_data(epochs_file, pokemons_file)
    plot_type_distribution(type_counts)

    epochs_file.close()
    best_teams_file.close()
    pokemons_file.close()


if __name__ == "__main__":
    main()
