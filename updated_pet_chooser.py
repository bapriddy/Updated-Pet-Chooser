# Updated Pet chooser 
import pymysql.cursors
from creds import *
from pets import Pets

# Connect to the database
try:
    myConnection = pymysql.connect(
        host=hostname,
        user=username,
        password=password,
        db=database,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    print("Database connection established.")

except Exception as e:
    print(f"An error has occurred while connecting to the database: {e}")
    exit()

# Create a list for pet objects
pet_list = []

# Retrieve SQL data
try:
    with myConnection.cursor() as cursor:
        sqlSelect = """
            SELECT pets.name, pets.animal_type_id, pets.age, owners.name as owner_name
            FROM pets
            LEFT JOIN owners ON pets.owner_id = owners.id;
        """
        cursor.execute(sqlSelect)

        rows = cursor.fetchall()

        if not rows:
            print("Sorry, no pets found in the database.")
        else:
            pet_list.clear()
            for row in rows:
                owner_name = row['owner_name'] if row['owner_name'] else "Unknown Owner"
                pet = Pets(row['name'], row['animal_type_id'], owner_name, row['age'])
                pet_list.append(pet)

except Exception as e:
    print(f"An error occurred while retrieving pet data from the database: {e}")

# Function to display pet list
def display_pet_choice():
    print("\nChoose a pet by entering the corresponding number or enter 'Q' to quit:")
    for index, pet in enumerate(pet_list, start=1):
        print(f"[{index}] {pet.name} - {pet.get_animal_type()}")

# Function to display the pet information
def display_pet_info(pet):
    print(f"\nYou have chosen {pet.name}, the {pet.get_animal_type()}. {pet.name} is {pet.age} years old. {pet.name}'s owner is {pet.owner}.")

# Function to edit pet details
def edit_pet_details(pet):
    print(f"\nYou have chosen to edit {pet.name}.")

    # Edit name
    new_name = input(f"New name: (current: {pet.name}) ")
    if new_name.strip():
        pet.name = new_name
        print(f"Pet's name has been updated to {pet.name}.")
        update_pet_in_db(pet)

    # Edit age (validate the input)
    while True:
        new_age = input(f"New age: (current: {pet.age}) ")
        if not new_age.strip():  # No change
            break
        if pet.is_valid_age(new_age):
            pet.age = int(new_age)
            print(f"Pet's age has been updated to {pet.age}.")
            update_pet_in_db(pet)
            break
        else:
            print("Invalid input. Please enter a valid positive integer for age.")

# Function to update pet in the database
def update_pet_in_db(pet):
    try:
        with myConnection.cursor() as cursor:
            sqlUpdate = """
                UPDATE pets
                SET name = %s, age = %s
                WHERE name = %s AND age = %s;
            """
            cursor.execute(sqlUpdate, (pet.name, pet.age, pet.name, pet.age))
            myConnection.commit()
    except Exception as e:
        print(f"Error updating pet in the database: {e}")

# Main loop for displaying pet choices and handling user input
while True:
    display_pet_choice()
    user_input = input("Enter a number to select a pet, or 'Q' to quit: ").strip()

    if user_input.lower() == 'q':
        print("Exiting the program. Goodbye!")
        break  # Exit the loop and the program

    try:
        number = int(user_input) - 1

        if 0 <= number < len(pet_list):
            pet_choice = pet_list[number]
            display_pet_info(pet_choice)

            # Prompt for further actions (Continue, Quit, or Edit)
            while True:
                action = input("\nWould you like to [C]ontinue, [Q]uit, or [E]dit this pet? ").strip().lower()
                if action == 'q':
                    print("Exiting the program. Goodbye!")
                    myConnection.close()
                    exit()
                elif action == 'c':
                    break  # Go back to the initial list of pets
                elif action == 'e':
                    edit_pet_details(pet_choice)
                    break  # After editing, go back to the initial list of pets
                else:
                    print("Invalid input. Please enter C, Q, or E.")

        else:
            print("Invalid choice. Please select a valid number from the list.")
    except ValueError:
        print("Invalid input. Please enter a number corresponding to your choice or 'Q' to quit.")

# Close the database connection when done
myConnection.close()
print("Database connection closed.")

