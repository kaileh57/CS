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

# Helper function to calculate gerbil excitement level
def calculate_excitement(num_gerbils, urgency):
    """Calculate how excited the gerbils are about this order"""
    base_excitement = int(num_gerbils) * 10
    urgency_multiplier = {"leisurely": 0.5, "standard": 1.0, "emergency": 3.0, "MAXIMUM_GERBIL_SPEED": 10.0}
    return int(base_excitement * urgency_multiplier.get(urgency, 1.0))

@app.route('/gerbilzon')
def gerbilzon():
    return render_template('gerbilzon.html.j2')

@app.route('/gerbil_order', methods=['POST'])
def gerbil_order():
    # Get form data
    customer_name = request.form.get('customer_name')
    email = request.form.get('email')
    num_gerbils = request.form.get('num_gerbils')
    delivery_time = request.form.get('delivery_time')
    urgency = request.form.get('urgency')
    theme_color = request.form.get('theme_color')
    special_instructions = request.form.get('special_instructions')
    accessories = request.form.getlist('accessories')

    # Server-side validation
    errors = []
    if not customer_name or customer_name.strip() == "":
        errors.append("Customer name is required!")
    if not email or email.strip() == "":
        errors.append("Email is required!")
    if not num_gerbils or int(num_gerbils) < 1:
        errors.append("You must order at least 1 gerbil!")
    if not delivery_time:
        errors.append("Please specify a delivery time!")
    if not urgency:
        errors.append("Please select delivery urgency!")

    if errors:
        return render_template('gerbilzon.html.j2', errors=errors)

    # Calculate excitement level using helper function
    excitement = calculate_excitement(num_gerbils, urgency)

    return render_template('gerbil_confirmation.html.j2',
                         customer_name=customer_name,
                         email=email,
                         num_gerbils=num_gerbils,
                         delivery_time=delivery_time,
                         urgency=urgency,
                         theme_color=theme_color,
                         special_instructions=special_instructions,
                         accessories=accessories,
                         excitement=excitement)