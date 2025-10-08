from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# THIS IS NOT CYBERSECURE, I KNOW, I should know better, but I'm lazy
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key=AIzaSyDg3bYNunnFphk9HcKDHv4vslcgAaJhRJE"

# Render le index page (doesn't need anything special, it should be a blank slate)
@app.route('/')
def index():
    return render_template('index.html.j2')

# Helper function to generate story with Gemini API, modified based on the Google Gemini docs
# I am not nearly trying to claim this as my own, it does not count as the function I wrote
def generate_story(prompt):
    data = {
        "system_instruction": {
            "parts": [{
                "text": "You are a creative storyteller for a choose-your-own-adventure game. Write engaging, descriptive paragraphs (3-5 sentences) that continue the story based on the user's choices. Never use markdown formatting. Always respond with plain text only. End each story segment naturally, ready for the player to make their next choice."
            }]
        },
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    response = requests.post(GEMINI_URL, json=data)
    if response.status_code == 200:
        result_data = response.json()
        return result_data['candidates'][0]['content']['parts'][0]['text']
    else:
        # They call me Mr. Error Handling
        return f"Error generating story: {response.status_code}"

# Helper function to build character description, I did actually write this one
def build_character_summary(name, age, character_class, starting_item, backstory):
    summary = f"{name}, a {age}-year-old {character_class}"
    if backstory and backstory.strip(): # Dug up this beautiful way to do this from python docs (say goodbye to whitespace)
        summary += f" with the following background: {backstory}"
    summary += f". They begin their adventure carrying a {starting_item}."
    return summary

# I've used this technique in the past, but basically the idea is that we don't HAVE to route to a page named after the route, we can just use it as a function to handle the request
@app.route('/start_adventure', methods=['GET'])
def start_adventure():
    # Get character creation form data
    name = request.args.get('name')
    age = request.args.get('age')
    character_class = request.args.get('character_class')
    starting_item = request.args.get('starting_item')
    backstory = request.args.get('backstory')
    theme_color = request.args.get('theme_color')
    # Server-side validation, as  requested
    errors = []
    if not name or name.strip() == "":
        errors.append("Character name is required!")
    
    # Validate age with proper error handling
    if not age:
        errors.append("Age is required!") # Overbuilt age handling
    else:
        try:
            age_int = int(age)
            if age_int < 1 or age_int > 999:
                errors.append("Age must be between 1 and 999!")
        except ValueError:
            errors.append("Age must be a valid number!")
    if not character_class:
        errors.append("Please select a character class!")
    if not starting_item or starting_item.strip() == "":
        errors.append("Starting item is required!")
    # Validate color format (should be hex color like #RRGGBB)
    if not theme_color:
        errors.append("Theme color is required!")
    elif not (len(theme_color) == 7 and theme_color.startswith('#')):
        errors.append("Invalid color format!")
    
    if errors:
        return render_template('index.html.j2', errors=errors) # Send them straight back to the index and tell them off
    # Build character summary using helper function
    character_info = build_character_summary(name, age, character_class, starting_item, backstory)
    # Generate the opening story
    opening_prompt = f"Start a fantasy adventure story. The main character is: {character_info}. Begin the story with them standing at a crossroads in a mysterious forest."
    story_text = generate_story(opening_prompt)
    # Initialize story history (we'll pass this along through forms)
    story_history = f"Character: {character_info}\n\n{story_text}"
    # Render the story page
    return render_template('story.html.j2', # Indent for readability
                         story_text=story_text,
                         story_history=story_history,
                         name=name,
                         theme_color=theme_color) # I don't really get why people make a whole other variable to just pass through a value

# Same note as above, but for the continue_story route
@app.route('/continue_story', methods=['GET'])
def continue_story():
    # Get the choice and story history
    choice = request.args.get('choice')
    story_history = request.args.get('story_history')
    name = request.args.get('name')
    theme_color = request.args.get('theme_color')
    # Server-side validation
    if not choice or choice.strip() == "":
        # If no choice provided, just show the current story
        # I felt like having an early return statement was more readable than tring to sandwhich it into the one below, and also I didn't think of that until now
        return render_template('story.html.j2',
                             story_text="You must make a choice to continue!",
                             story_history=story_history,
                             name=name,
                             theme_color=theme_color) 
    # Generate next part of story based on choice
    prompt = f"Previous story:\n{story_history}\n\nThe player chose: {choice}\n\nContinue the story based on this choice."
    new_story_text = generate_story(prompt)
    # Update story history
    updated_history = f"{story_history}\n\nPlayer's choice: {choice}\n\n{new_story_text}"
    return render_template('story.html.j2',
                         story_text=new_story_text,
                         story_history=updated_history,
                         name=name,
                         theme_color=theme_color)
