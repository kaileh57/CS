from flask import Flask, render_template, request

#set the recusion limit higher
import sys
sys.setrecursionlimit(30000)
sys.set_int_max_str_digits(20000)

app = Flask(__name__) #this has 2 underscores on each side

@app.route('/')
def index():
        return render_template('index.html.j2', name="Kellen")

@app.route('/results', methods=['POST'])
def resultsPage():
    full_name = request.form.get('full_name')
    sushi = request.form.get('sushi')
    vehicles = request.form.getlist('vehicle')
    return render_template('results.html.j2', full_name=full_name, sushi=sushi, vehicles=vehicles)

@app.route('/pokemonInfo')
def pokemonInfo():
    pokemonData = {'pikachu': 'Pikarchu is an Electric-type Pokémon introduced in Generation I. It evolves from Pichu when leveled up with high friendship and evolves into Raichu when exposed to a Thunder Stone.',
                   'charmander': 'Charmander is a Fire-type Pokémon introduced in Generation I. It evolves into Charmeleon starting at level 16, which then evolves into Charizard starting at level 36.',
                   'bulbasaur': 'Bulbasaur is a dual-type Grass/Poison Pokémon introduced in Generation I. It evolves into Ivysaur starting at level 16, which then evolves into Venusaur starting at level 32.'}
    whichPokemon = request.values.get("pokemon")

    # Server-side input validation
    if not whichPokemon:
        text = "Error: No Pokémon name provided."
    elif whichPokemon.lower() not in pokemonData:
        text = f"Error: '{whichPokemon}' is not a valid Pokémon name. Valid options are: {', '.join(pokemonData.keys())}."
    else:
        text = pokemonData[whichPokemon.lower()]

    return render_template('pokemonInfo.html.j2', text=text)