import streamlit as st
import pandas as pd
import os
import json
from PIL import Image
import io
import base64
import datetime

# Set page configuration
st.set_page_config(
    page_title="Food Recipe Application",
    page_icon="🍲",
    layout="wide"
)

# File paths for persistent storage
USER_DATA_FILE = "user_data.json"
RECIPE_DATA_FILE = "recipe_data.json"
FAVORITES_DATA_FILE = "favorites_data.json"

# Create data directory if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")

USER_DATA_FILE = os.path.join("data", USER_DATA_FILE)
RECIPE_DATA_FILE = os.path.join("data", RECIPE_DATA_FILE)
FAVORITES_DATA_FILE = os.path.join("data", FAVORITES_DATA_FILE)

# Initialize session state variables if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'recipes' not in st.session_state:
    st.session_state.recipes = {}
if 'user_favorites' not in st.session_state:
    st.session_state.user_favorites = {}

# Load data from JSON files
def load_data():
    # Load users
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            st.session_state.users = json.load(f)
    else:
        st.session_state.users = {"demo": "password"}  # Default user
        save_user_data()
    
    # Load recipes
    if os.path.exists(RECIPE_DATA_FILE):
        with open(RECIPE_DATA_FILE, 'r') as f:
            st.session_state.recipes = json.load(f)
    else:
        # Sample recipes with enhanced ingredient structure
        st.session_state.recipes = {
            "Pasta Carbonara": {
                "ingredients": [
                    {"name": "Pasta", "image": None},
                    {"name": "Eggs", "image": None},
                    {"name": "Cheese", "image": None},
                    {"name": "Bacon", "image": None}
                ],
                "instructions": "1. Boil pasta\n2. Cook bacon\n3. Mix eggs and cheese\n4. Combine all ingredients",
                "image": None,
                "author": "system",
                "date_added": str(datetime.datetime.now())
            },
            "Chicken Curry": {
                "ingredients": [
                    {"name": "Chicken", "image": None},
                    {"name": "Curry Paste", "image": None},
                    {"name": "Coconut Milk", "image": None},
                    {"name": "Rice", "image": None}
                ],
                "instructions": "1. Cook chicken\n2. Add curry paste\n3. Pour coconut milk\n4. Simmer and serve with rice",
                "image": None,
                "author": "system",
                "date_added": str(datetime.datetime.now())
            }
        }
        save_recipe_data()
    
    # Load favorites
    if os.path.exists(FAVORITES_DATA_FILE):
        with open(FAVORITES_DATA_FILE, 'r') as f:
            st.session_state.user_favorites = json.load(f)
    else:
        st.session_state.user_favorites = {}
        save_favorites_data()

# Save functions
def save_user_data():
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(st.session_state.users, f)

def save_recipe_data():
    with open(RECIPE_DATA_FILE, 'w') as f:
        json.dump(st.session_state.recipes, f)

def save_favorites_data():
    with open(FAVORITES_DATA_FILE, 'w') as f:
        json.dump(st.session_state.user_favorites, f)

# Function to handle login
def login():
    st.header("Login")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col1_1, col1_2 = st.columns(2)
        
        with col1_1:
            if st.button("Login", use_container_width=True):
                if username in st.session_state.users and st.session_state.users[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(f"Welcome {username}!")
                    # Initialize favorites for new users
                    if username not in st.session_state.user_favorites:
                        st.session_state.user_favorites[username] = []
                        save_favorites_data()
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        with col1_2:
            if st.button("Register", use_container_width=True):
                if username and password:
                    if username not in st.session_state.users:
                        st.session_state.users[username] = password
                        st.session_state.user_favorites[username] = []
                        save_user_data()
                        save_favorites_data()
                        st.success("Registration successful! You can now log in.")
                    else:
                        st.error("Username already exists")
                else:
                    st.error("Please provide both username and password")
    
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/5925/5925659.png", width=200)
        st.markdown("### Welcome to Recipe Hub!")
        st.write("Login to access your favorite recipes or register for a new account.")

# Function to search recipes
def search_recipe():
    st.header("Search Recipes")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input("Search by name or ingredient")
    
    with col2:
        sort_option = st.selectbox("Sort by", ["Name (A-Z)", "Name (Z-A)", "Newest First", "Oldest First"])
    
    if search_term or not search_term:  # Always show results
        results = []
        for name, details in st.session_state.recipes.items():
            # Search in recipe name or ingredient names
            if not search_term or search_term.lower() in name.lower() or any(search_term.lower() in ingredient["name"].lower() for ingredient in details["ingredients"]):
                results.append((name, details))
        
        # Sort results based on selection
        if sort_option == "Name (A-Z)":
            results.sort(key=lambda x: x[0])
        elif sort_option == "Name (Z-A)":
            results.sort(key=lambda x: x[0], reverse=True)
        elif sort_option == "Newest First":
            results.sort(key=lambda x: x[1].get("date_added", ""), reverse=True)
        elif sort_option == "Oldest First":
            results.sort(key=lambda x: x[1].get("date_added", ""))
        
        if results:
            st.write(f"Found {len(results)} recipes")
            
            # Display results in a grid
            cols = st.columns(3)
            for i, (name, details) in enumerate(results):
                with cols[i % 3]:
                    st.subheader(name)
                    if details["image"]:
                        try:
                            st.image(base64.b64decode(details["image"]), caption=name, width=200)
                        except:
                            st.info("Image could not be displayed")
                    else:
                        st.image("https://cdn-icons-png.flaticon.com/512/3565/3565418.png", width=150)
                    
                    with st.expander("View Details"):
                        st.write("**Ingredients:**")
                        for ing in details["ingredients"]:
                            st.write(f"• {ing['name']}")
                            if ing["image"]:
                                try:
                                    st.image(base64.b64decode(ing["image"]), width=100)
                                except:
                                    st.info(f"Image for {ing['name']} could not be displayed")
                        
                        st.write("**Instructions:**")
                        st.write(details["instructions"])
                        
                        st.write(f"**Created by:** {details['author']}")
                        
                        # Save to favorite button
                        if st.button(f"Save to Favorites", key=f"fav_{name}"):
                            if st.session_state.username not in st.session_state.user_favorites:
                                st.session_state.user_favorites[st.session_state.username] = []
                            
                            if name not in st.session_state.user_favorites[st.session_state.username]:
                                st.session_state.user_favorites[st.session_state.username].append(name)
                                save_favorites_data()
                                st.success(f"Added {name} to favorites!")
                                st.rerun()
                            else:
                                st.info(f"{name} is already in your favorites")
        else:
            st.info("No recipes found matching your search")

# Function to type/add new recipes
def type_recipe():
    st.header("Add New Recipe")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        recipe_name = st.text_input("Recipe Name")
        
        # Dynamic ingredients input
        st.subheader("Ingredients")
        if "ingredients_list" not in st.session_state:
            st.session_state.ingredients_list = [{"name": "", "image": None}]
        
        for i, ingredient in enumerate(st.session_state.ingredients_list):
            cols = st.columns([3, 1])
            with cols[0]:
                st.session_state.ingredients_list[i]["name"] = st.text_input(f"Ingredient {i+1}", 
                                                                          value=ingredient["name"], 
                                                                          key=f"ing_name_{i}")
            with cols[1]:
                if st.button("Remove", key=f"remove_ing_{i}"):
                    st.session_state.ingredients_list.pop(i)
                    st.rerun()
        
        if st.button("Add Ingredient"):
            st.session_state.ingredients_list.append({"name": "", "image": None})
            st.rerun()
        
        instructions = st.text_area("Instructions")
    
    with col2:
        st.write("Upload an image of your recipe:")
        uploaded_image = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
        image_data = None
        
        if uploaded_image is not None:
            image = Image.open(uploaded_image)
            st.image(image, caption="Uploaded Image", width=300)
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            image_data = base64.b64encode(buf.getvalue()).decode()
    
    if st.button("Save Recipe", use_container_width=True):
        if recipe_name and any(ing["name"].strip() for ing in st.session_state.ingredients_list):
            # Filter out empty ingredients
            valid_ingredients = [ing for ing in st.session_state.ingredients_list if ing["name"].strip()]
            
            st.session_state.recipes[recipe_name] = {
                "ingredients": valid_ingredients,
                "instructions": instructions,
                "image": image_data,
                "author": st.session_state.username,
                "date_added": str(datetime.datetime.now())
            }
            save_recipe_data()
            st.success(f"Recipe '{recipe_name}' saved successfully!")
            # Clear the ingredients list for next recipe
            st.session_state.ingredients_list = [{"name": "", "image": None}]
            st.rerun()
        else:
            st.error("Please provide at least a recipe name and one ingredient")

# Function to take pictures of ingredients
def take_ingredient_photo():
    st.header("Add Ingredient Photos")
    
    recipe_options = list(st.session_state.recipes.keys())
    
    if not recipe_options:
        st.info("No recipes available. Please create a recipe first.")
        return
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        recipe_to_update = st.selectbox("Select Recipe", recipe_options)
        
        if recipe_to_update:
            # Get ingredients for the selected recipe
            ingredients = st.session_state.recipes[recipe_to_update]["ingredients"]
            ingredient_names = [ing["name"] for ing in ingredients]
            
            if ingredient_names:
                ingredient_to_update = st.selectbox("Select Ingredient", ingredient_names)
                
                if ingredient_to_update:
                    st.write(f"Adding photo for **{ingredient_to_update}** in recipe **{recipe_to_update}**")
            else:
                st.info("This recipe doesn't have any ingredients. Please add ingredients first.")
                return
    
    with col2:
        uploaded_image = st.file_uploader("Upload an ingredient image", type=["jpg", "jpeg", "png"])
        
        if uploaded_image is not None and ingredient_to_update:
            image = Image.open(uploaded_image)
            st.image(image, caption=f"Image for {ingredient_to_update}", width=250)
            
            if st.button("Add Ingredient Photo"):
                # Find the ingredient in the recipe and update its image
                for i, ing in enumerate(st.session_state.recipes[recipe_to_update]["ingredients"]):
                    if ing["name"] == ingredient_to_update:
                        # Convert image to base64
                        buf = io.BytesIO()
                        image.save(buf, format="PNG")
                        image_data = base64.b64encode(buf.getvalue()).decode()
                        
                        # Update the ingredient image
                        st.session_state.recipes[recipe_to_update]["ingredients"][i]["image"] = image_data
                        save_recipe_data()
                        
                        st.success(f"Photo added for {ingredient_to_update} in {recipe_to_update}!")
                        
                        # Display the updated ingredients
                        st.write(f"**Updated Ingredients for {recipe_to_update}:**")
                        for ing in st.session_state.recipes[recipe_to_update]["ingredients"]:
                            st.write(f"• {ing['name']}")
                            if ing["name"] == ingredient_to_update:
                                st.image(image, width=100)
                        
                        break

# Function to manage favorite recipes
def manage_favorites():
    st.header("Manage Favorite Recipes")
    
    if st.session_state.username in st.session_state.user_favorites and st.session_state.user_favorites[st.session_state.username]:
        favorites = st.session_state.user_favorites[st.session_state.username]
        
        st.write(f"You have {len(favorites)} favorite recipes")
        
        # Display favorites in a grid
        cols = st.columns(3)
        for i, recipe_name in enumerate(favorites):
            if recipe_name in st.session_state.recipes:
                with cols[i % 3]:
                    details = st.session_state.recipes[recipe_name]
                    st.subheader(recipe_name)
                    if details["image"]:
                        try:
                            st.image(base64.b64decode(details["image"]), caption=recipe_name, width=200)
                        except:
                            st.info("Image could not be displayed")
                    else:
                        st.image("https://cdn-icons-png.flaticon.com/512/3565/3565418.png", width=150)
                    
                    with st.expander("View Details"):
                        st.write("**Ingredients:**")
                        for ing in details["ingredients"]:
                            st.write(f"• {ing['name']}")
                            if ing["image"]:
                                try:
                                    st.image(base64.b64decode(ing["image"]), width=100)
                                except:
                                    st.info(f"Image for {ing['name']} could not be displayed")
                        
                        st.write("**Instructions:**")
                        st.write(details["instructions"])
                        
                        st.write(f"**Created by:** {details['author']}")
                        
                        # Remove from favorites button
                        if st.button(f"Remove from Favorites", key=f"remove_{recipe_name}"):
                            st.session_state.user_favorites[st.session_state.username].remove(recipe_name)
                            save_favorites_data()
                            st.success(f"Removed {recipe_name} from favorites!")
                            st.rerun()
    else:
        st.info("You don't have any favorite recipes yet. Search for recipes and add them to your favorites!")
        st.image("https://cdn-icons-png.flaticon.com/512/2772/2772128.png", width=200)

# Function to share recipes
def share_recipe():
    st.header("Share Recipe")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        if st.session_state.username in st.session_state.user_favorites and st.session_state.user_favorites[st.session_state.username]:
            favorites = st.session_state.user_favorites[st.session_state.username]
            recipe_to_share = st.selectbox("Select Recipe to Share", favorites)
            
            share_method = st.radio("Share via:", ["Email", "Link", "Social Media"])
            
            if st.button("Generate Sharing Link"):
                share_link = f"https://recipe-hub.com/shared/{recipe_to_share.replace(' ', '-').lower()}"
                st.success("Recipe Shared Successfully!")
                st.code(share_link)
                
                if share_method == "Email":
                    st.write("Email with recipe details has been prepared!")
                elif share_method == "Social Media":
                    st.write("Ready to post on your social media!")
                
                # Display the recipe card
                if recipe_to_share in st.session_state.recipes:
                    details = st.session_state.recipes[recipe_to_share]
                    st.subheader(f"Preview: {recipe_to_share}")
                    if details["image"]:
                        try:
                            st.image(base64.b64decode(details["image"]), width=300)
                        except:
                            st.info("Image could not be displayed")
                    st.write("**Ingredients:**")
                    for ing in details["ingredients"]:
                        st.write(f"• {ing['name']}")
                        if ing["image"]:
                            try:
                                st.image(base64.b64decode(ing["image"]), width=100)
                            except:
                                st.info(f"Image for {ing['name']} could not be displayed")
                    st.write("**Instructions:**")
                    st.write(details["instructions"])
        else:
            st.info("You need to add recipes to your favorites before you can share them")
    
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3991/3991833.png", width=220)
        st.write("Share your favorite recipes with friends and family!")

# Function to sync favorites
def sync_favorites():
    st.header("Favorite Recipe Sync")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.write("Sync your favorite recipes across all your devices")
        st.write("Your account: **" + st.session_state.username + "**")
        
        device_name = st.text_input("Device Name (e.g., My Phone, My Laptop)")
        
        sync_options = st.multiselect("Sync Options", 
                                      ["Favorites", "Your Created Recipes", "Recipe Images", "Ingredient Images"],
                                      default=["Favorites", "Ingredient Images"])
        
        if st.button("Sync Now"):
            with st.spinner("Syncing your recipes..."):
                # Simulate sync with a delay
                import time
                time.sleep(1.5)
                st.success("Sync completed successfully!")
                
                # Show what was synced
                st.write("**Synced Items:**")
                if "Favorites" in sync_options:
                    if st.session_state.username in st.session_state.user_favorites:
                        num_favorites = len(st.session_state.user_favorites[st.session_state.username])
                        st.write(f"✓ {num_favorites} favorite recipes")
                    else:
                        st.write("✓ 0 favorite recipes")
                
                if "Your Created Recipes" in sync_options:
                    created_recipes = [r for r, details in st.session_state.recipes.items() 
                                      if details["author"] == st.session_state.username]
                    st.write(f"✓ {len(created_recipes)} created recipes")
                
                if "Recipe Images" in sync_options:
                    img_count = sum(1 for r in st.session_state.recipes.values() if r["image"] is not None)
                    st.write(f"✓ {img_count} recipe images")
                
                if "Ingredient Images" in sync_options:
                    ing_img_count = 0
                    for recipe in st.session_state.recipes.values():
                        for ing in recipe["ingredients"]:
                            if ing["image"] is not None:
                                ing_img_count += 1
                    st.write(f"✓ {ing_img_count} ingredient images")
    
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/2682/2682067.png", width=220)
        st.write("Keep your recipes synchronized across all your devices!")

# Main app layout
def main():
    # Load data first
    load_data()
    
    st.title("🍲 Food Recipe Application")
    
    # Create a sidebar for navigation
    st.sidebar.title("Navigation")
    
    if not st.session_state.logged_in:
        login()
    else:
        st.sidebar.write(f"**Logged in as:** {st.session_state.username}")
        
        # Add logout button
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
        
        # Navigation options
        option = st.sidebar.radio(
            "Choose an option",
            ["Search Recipe", "Type New Recipe", "Add Ingredient Photos", 
             "Manage Favorites", "Share Recipe", "Sync Favorites"]
        )
        
        # Display user stats in sidebar
        st.sidebar.markdown("---")
        st.sidebar.subheader("Your Recipe Stats")
        
        # Count user's recipes
        user_recipes = len([r for r, details in st.session_state.recipes.items() 
                           if details["author"] == st.session_state.username])
        
        # Count favorites
        user_favorites = 0
        if st.session_state.username in st.session_state.user_favorites:
            user_favorites = len(st.session_state.user_favorites[st.session_state.username])
        
        # Count ingredient images
        ingredient_images = 0
        for recipe in st.session_state.recipes.values():
            if recipe["author"] == st.session_state.username:
                for ing in recipe["ingredients"]:
                    if ing["image"] is not None:
                        ingredient_images += 1
        
        st.sidebar.write(f"📝 Created Recipes: {user_recipes}")
        st.sidebar.write(f"⭐ Favorite Recipes: {user_favorites}")
        st.sidebar.write(f"🖼️ Ingredient Images: {ingredient_images}")
        st.sidebar.write(f"🔄 Last Sync: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Display selected option
        if option == "Search Recipe":
            search_recipe()
        elif option == "Type New Recipe":
            type_recipe()
        elif option == "Add Ingredient Photos":
            take_ingredient_photo()
        elif option == "Manage Favorites":
            manage_favorites()
        elif option == "Share Recipe":
            share_recipe()
        elif option == "Sync Favorites":
            sync_favorites()

if __name__ == "__main__":
    main()