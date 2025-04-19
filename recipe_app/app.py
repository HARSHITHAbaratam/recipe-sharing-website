import streamlit as st
import pandas as pd
import os
from PIL import Image
import io
import base64

# Set page configuration
st.set_page_config(
    page_title="Food Recipe Application",
    page_icon="🍲",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'users' not in st.session_state:
    st.session_state.users = {"demo": "password"}  # Demo user
if 'recipes' not in st.session_state:
    # Sample recipes
    st.session_state.recipes = {
        "Pasta Carbonara": {
            "ingredients": ["Pasta", "Eggs", "Cheese", "Bacon"],
            "instructions": "1. Boil pasta\n2. Cook bacon\n3. Mix eggs and cheese\n4. Combine all ingredients",
            "image": None,
            "author": "system"
        },
        "Chicken Curry": {
            "ingredients": ["Chicken", "Curry Paste", "Coconut Milk", "Rice"],
            "instructions": "1. Cook chicken\n2. Add curry paste\n3. Pour coconut milk\n4. Simmer and serve with rice",
            "image": None,
            "author": "system"
        }
    }
if 'user_favorites' not in st.session_state:
    st.session_state.user_favorites = {}

# Function to handle login
def login():
    st.header("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        if username in st.session_state.users and st.session_state.users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome {username}!")
            # Initialize favorites for new users
            if username not in st.session_state.user_favorites:
                st.session_state.user_favorites[username] = []
            st.rerun()
        else:
            st.error("Invalid username or password")
    
    if st.button("Register"):
        if username and password:
            if username not in st.session_state.users:
                st.session_state.users[username] = password
                st.session_state.user_favorites[username] = []
                st.success("Registration successful! You can now log in.")
            else:
                st.error("Username already exists")
        else:
            st.error("Please provide both username and password")

# Function to search recipes
def search_recipe():
    st.header("Search Recipes")
    search_term = st.text_input("Search by name or ingredient")
    
    if search_term:
        results = []
        for name, details in st.session_state.recipes.items():
            if search_term.lower() in name.lower() or any(search_term.lower() in ingredient.lower() for ingredient in details["ingredients"]):
                results.append((name, details))
        
        if results:
            for name, details in results:
                with st.expander(name):
                    st.write("Ingredients:")
                    st.write(", ".join(details["ingredients"]))
                    st.write("Instructions:")
                    st.write(details["instructions"])
                    if details["image"]:
                        st.image(base64.b64decode(details["image"]), caption="Recipe Image")
                    
                    # Save to favorite button
                    if st.button(f"Save to Favorites", key=f"fav_{name}"):
                        if name not in st.session_state.user_favorites[st.session_state.username]:
                            st.session_state.user_favorites[st.session_state.username].append(name)
                            st.success(f"Added {name} to favorites!")
                            st.rerun()
                        else:
                            st.info(f"{name} is already in your favorites")
        else:
            st.info("No recipes found matching your search")

# Function to type/add new recipes
def type_recipe():
    st.header("Add New Recipe")
    recipe_name = st.text_input("Recipe Name")
    
    ingredients = st.text_area("Ingredients (one per line)")
    instructions = st.text_area("Instructions")
    
    uploaded_image = st.file_uploader("Upload an image of the recipe (optional)", type=["jpg", "jpeg", "png"])
    image_data = None
    
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", width=300)
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        image_data = base64.b64encode(buf.getvalue()).decode()
    
    if st.button("Save Recipe"):
        if recipe_name and ingredients:
            ingredients_list = [ing.strip() for ing in ingredients.split("\n") if ing.strip()]
            st.session_state.recipes[recipe_name] = {
                "ingredients": ingredients_list,
                "instructions": instructions,
                "image": image_data,
                "author": st.session_state.username
            }
            st.success(f"Recipe '{recipe_name}' saved successfully!")
            st.rerun()
        else:
            st.error("Please provide at least a recipe name and ingredients")

# Function to take pictures of ingredients
def take_ingredient_photo():
    st.header("Take Pictures of Ingredients")
    st.write("This feature allows you to take photos of ingredients and add them to your recipe.")
    
    recipe_options = list(st.session_state.recipes.keys())
    recipe_to_update = st.selectbox("Select Recipe to Add Ingredient Photo", recipe_options)
    
    ingredient_name = st.text_input("Ingredient Name")
    
    uploaded_image = st.file_uploader("Upload an ingredient image", type=["jpg", "jpeg", "png"])
    
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Ingredient", width=300)
        
        if st.button("Add Ingredient Photo"):
            # In a real app, you'd store this image and link it to the recipe/ingredient
            st.success(f"Photo added for {ingredient_name} in {recipe_to_update}!")
            # This is a simplified implementation - in a real app you'd update the recipe with the ingredient photo

# Function to manage favorite recipes
def manage_favorites():
    st.header("Manage Favorite Recipes")
    
    if st.session_state.username in st.session_state.user_favorites and st.session_state.user_favorites[st.session_state.username]:
        favorites = st.session_state.user_favorites[st.session_state.username]
        
        for recipe_name in favorites:
            if recipe_name in st.session_state.recipes:
                with st.expander(recipe_name):
                    details = st.session_state.recipes[recipe_name]
                    st.write("Ingredients:")
                    st.write(", ".join(details["ingredients"]))
                    st.write("Instructions:")
                    st.write(details["instructions"])
                    if details["image"]:
                        st.image(base64.b64decode(details["image"]), caption="Recipe Image")
                    
                    # Remove from favorites button
                    if st.button(f"Remove from Favorites", key=f"remove_{recipe_name}"):
                        st.session_state.user_favorites[st.session_state.username].remove(recipe_name)
                        st.success(f"Removed {recipe_name} from favorites!")
                        st.rerun()
    else:
        st.info("You don't have any favorite recipes yet. Search for recipes and add them to your favorites!")

# Function to share recipes
def share_recipe():
    st.header("Share Recipe")
    
    if st.session_state.username in st.session_state.user_favorites and st.session_state.user_favorites[st.session_state.username]:
        favorites = st.session_state.user_favorites[st.session_state.username]
        recipe_to_share = st.selectbox("Select Recipe to Share", favorites)
        
        share_link = f"https://yourrecipeportal.com/recipe/{recipe_to_share.replace(' ', '-').lower()}"
        st.success("Recipe Shared Successfully!")
        st.code(share_link)
        st.write("Share this link with your friends so they can view your recipe!")
        
        # In a real app, you'd implement actual sharing functionality here
    else:
        st.info("You need to add recipes to your favorites before you can share them")

# Function to sync favorites
def sync_favorites():
    st.header("Favorite Recipe Sync")
    st.write("This feature allows you to sync your favorite recipes across devices.")
    
    if st.button("Sync Now"):
        # In a real app, this would connect to a cloud service
        st.success("Favorites synchronized successfully!")
        st.info("All your favorite recipes are now updated across your devices")

# Main app layout
def main():
    st.title("Food Recipe Application")
    
    # Create a sidebar for navigation
    st.sidebar.title("Navigation")
    
    if not st.session_state.logged_in:
        login()
    else:
        st.sidebar.write(f"Logged in as: {st.session_state.username}")
        
        # Add logout button
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
        
        # Navigation options
        option = st.sidebar.radio(
            "Choose an option",
            ["Search Recipe", "Type New Recipe", "Take Ingredient Photos", 
             "Manage Favorites", "Share Recipe", "Sync Favorites"]
        )
        
        if option == "Search Recipe":
            search_recipe()
        elif option == "Type New Recipe":
            type_recipe()
        elif option == "Take Ingredient Photos":
            take_ingredient_photo()
        elif option == "Manage Favorites":
            manage_favorites()
        elif option == "Share Recipe":
            share_recipe()
        elif option == "Sync Favorites":
            sync_favorites()

if __name__ == "__main__":
    main()