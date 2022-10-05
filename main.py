from flask import Flask, request, render_template
import pandas as pd
import requests
import config

app = Flask(__name__)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/', methods=['POST', 'GET'])  #Flask app
def root_page(): # main page with search function will ask for user input
    ingredient = ''     # user's ingredient for searching on
    max_time = ''       # user's cooking & prep time limit
    cuisine = ''        # cuisine type
    health = ''         # health to represent the dietary requirements
    if request.method == 'POST' and ('userfood' and 'usertime' and 'usercuisine' and 'userhealth') in request.form: # Once acquired inputs index html will update itself
        ingredient = request.form.get('userfood')       # ingredient input
        max_time = int(request.form.get('usertime'))    # preparation time converted to a string
        cuisine = request.form.get('usercuisine')       # cuisine type (e.g. Chinese, Eastern European)
        health = request.form.get('userhealth')         # health label (e.g. vegan, gluten-free)
        recipe_search(ingredient, max_time, cuisine, health)
        run_csv(ingredient, max_time, cuisine, health)
    return render_template("index.html", ingredient=ingredient, max_time=max_time, cuisine=cuisine, health=health) # html with the objects connected to the html file type


@app.route('/recipes', methods=['GET', 'POST'])     # list of recipes website
def recipes_html():
    return render_template('recipes.html')

def recipe_search(ingredient, max_time, cuisine, health): # all user inputs which will then retrieve the features from the api database
    app_id = config.app_id # accessible from the config.py hidden to not keep public
    app_key = config.app_key
    #id and key required to access the database from https://developer.edamam.com/
    if health == 'none':  # does not need to have a dietary input
        result = requests.get(
        'https://api.edamam.com/search?q={}&app_id={}&app_key={}&time=1-{}&cuisineType={}'.format(ingredient, app_id, app_key, max_time, cuisine)) # users inputs as filters, main is the ingredient
    else:
        result = requests.get('https://api.edamam.com/search?q={}&app_id={}&app_key={}&time=1-{}&cuisineType={}&health={}'.format(ingredient, app_id, app_key, max_time, cuisine, health))
    data = result.json()
    return data['hits']
    # API documentation and search query requests https://developer.edamam.com/edamam-docs-recipe-api

def run_csv(ingredient, max_time, cuisine, health):   #append results to a csv file and then convert to html to show a table on the website
    d = []  # clear the dataset whenever run_csv used for fresh table
    # ingredient = input('Enter an ingredient: ')
    results = recipe_search(ingredient, max_time, cuisine, health)

    if results != []:             # if the search result is not empty table is created
        for item in results:
            recipe = item['recipe']
            label = recipe['label']
            cuisine = str(recipe['cuisineType'])  # convert to string
            allowed_chars = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ ,') # allows the cuisine type to be spelt out correctly
            # characters allowed letters and commas
            cuisine = ''.join(filter(allowed_chars.__contains__, cuisine))
            # extract allowed characters from search input, as set out from the above

            calories = round(recipe['calories'])        # round numbers to whole number for each number value, calories per meal
            carbs = round(recipe['totalNutrients']['CHOCDF']['quantity'])  # grams of carbohydrates
            fat = round(recipe['totalNutrients']['FAT']['quantity'])  # grams of fat
            protein = round(recipe['totalNutrients']['PROCNT']['quantity'])  # grams of protein

            # total time to prep and cook the recipe
            time = round(recipe['totalTime'])
            link = recipe['url']
            # creating csv files with data from the API database
            d.append(
                {
                    'Search term': ingredient,
                    'Recipe name': label,
                    'Cuisine Type': cuisine,
                    'Diet type': health,
                    'Total time': time,
                    'Calories': calories,
                    'Carbohydrates': carbs,
                    'Fat': fat,
                    'Protein': protein,
                    'URL': link,
                }
            )
        recipe_df = pd.DataFrame(d) # recipe search creates the database
        recipe_df.to_csv('recipe-search.csv', index=False) # makes the csv file
        oranges_recipes = pd.read_csv('recipe-search.csv')       # Read the csv file
        oranges_recipes['URL'] = '<a href=' + oranges_recipes['URL'] + '><div>' + oranges_recipes['URL'] + '</div></a>'
        # hyperlink
        oranges_recipes.to_html('./templates/recipes.html', escape=False)
        # convert to a recipes.HTML page
        # escape=False needed for hyperlink to render

    else:
        print('No search results!')

# If search result is empty print a message to the console and don't run the rest of the program.
# The recipes.html page will not be regenerated but the user will see the previous results.
# spelling varies from country to country and some recipe names are misspelt anyway.

app.run()

if __name__ == '__main__':
  app.run(debug=True)