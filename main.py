import streamlit as st
import re
import pandas as pd
import json

class Contact:
    def __init__ (self, name, phone, email, category, favorite=False):
        phone_pattern = r'^\+?\d{10,15}'
        
        if not re.match(phone_pattern, phone):
            raise ValueError("Invalid phone number format")
        
        email_pattern = r'^\w{1,50}@\w{1,50}\.(com|net|org)$'
        
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email number format")

        self.name = name
        self.phone = phone
        self.email = email
        self.category = category
        self.favorite = favorite
        
if "contact_list" not in st.session_state:
    st.session_state.contact_list = []

if " filename" not in st.session_state:
    st.session_state.filename = []

if "category" not in st.session_state:
    st.session_state.category = ["General", "Family", "Friends", "Work"]

# Add new  contact
def add_contact(contact):

    st.session_state.contact_list.append(contact)
    return f"{contact.name} has been added to the list"

 #View all contacts   
def view_all_contacts():
        contacts = []

        for contact in st.session_state.contact_list:
            contacts.append({
                "Name": contact.name,
                "Phone": contact.phone,
                "Email": contact.email,
                "category": contact.category,
                "Favorite": "Yes" if contact.favorite else "No"
            })
        
        return contacts

# Search contacts
def search_contact(query):
    if st.session_state.contact_list:
        return []
    query = query.lower() if query else ""
    search_results = []

    if not query:
        return []
    
    for contact in st.session_state.contact_list:
        if (query in contact.name.lower() or query in contact.phone
            or query in contact.email.lower()) :

            search_results.append({
                "Name": contact.name,
                "Phone": contact.phone,
                "Email": contact.email,
                "Category": contact.category,
                "Favorite": "Yes" if contact.favorite else "N"
            })

    return search_results

# Delete contacts
def delete_contact(index):
    if 0 <= index < len(st.session_state.contact_list):
        contact = st.session_state.contact_list[index]
        del st.session_state.contact_list[index]
        return f"Contact {contact.name} deleted successfully"
    return "Invalid contact index"

# File Operations
def save_contacts_to_file(filename):
    if not filename:
        return "Please provide a filename"
    
    contact_data = []
    for contact in st.session_state.contact_list:
        contact_data.append({
            "Name": contact.name,
            "Phone": contact.phone,
            "Email": contact.email,
            "Category": contact.category,
            "Favorite": contact.favorite
        })
    
    contact_df = pd.DataFrame(contact_data)

    try:
        contact_df.to_csv(f"{filename}.csv", index=False)
        return f"Contacts saved to {filename}.csv"
    except Exception as e:
        return f"Error saving file: {e}"
    
def load_contact_from_file(filename):
    try:
        df = pd.read_csv(f"{filename}.csv")
        st.session_state.contact_list = []

        for _, row in df.iterrows():
            try:
                favorite_val = row.get('Favorite', False)
                if isinstance(favorite_val, str):
                    favorite_val = (favorite_val.lower() == 'yes' or favorite_val.lower() == 'true')

                contact = Contact(row['Name', row['Phone'], row['Email']],
                                  category=row.get('Category', 'General'),
                                  favorite=favorite_val)
                st.session_state.contact_list.append(contact)
            except ValueError as e:
                st.warning(f"Skipping Invalid contact: {e}")

        return f"Loaded {len(st.session_state.contact_list)} contacts from {filename}.csv"
    except FileNotFoundError:
        return f"File {filename}.csv not found"    
    except Exception as e:
        return f"Error loading file: {e}"

# Edit Contact
def update_contact(index, name, phone, email):
    if 0 <= index < len(st.session_state.contact_list):
        try:
            updated_contact = Contact(name, phone, email)
            
            st.session_state.contact_list[index] = updated_contact

            return f"Contact updated successfully"
        except ValueError as e:
            return f"Error updating contact {e}"
    return "Invalid contact index"

# Add category
def add_category(name):
    if not st.session_state.contact_list:
        return f"No Contacts. Please add contacts first"
    
    if not name in st.session_state.category:
        st.session_state.category.append(name)
        return f"Category {name} has been added to the list"
    else:
        return f"Category already exists"

# Add to favorite
def add_to_favorite(index):
    if st.session_state.contact_list:
        return f"No contacts available. Please add contacts first"
    
    if 0 < index < len(st.session_state.contact_list):
        contact = st.session_state.contact_list[index]

        contact.favorite = True
        return f"{contact.name} added to facorites"
    else:
        return "Invalid contact index"

def filter_favorite():
    if st.session_state.contact_list:
        return []
    
    favorite_data = []

    for contact in st.session_state.contact_list:

        if contact.favorite:
            favorite_data.append({
                "Name": contact.name,
                "Phone": contact.phone,
                "Email": contact.email
            })

    return favorite_data

# Sort contacts
def sort_contacts(field, ascending=True):
    if st.session_state.contact_list:
        return []
    
    sorted_contacts = sorted(
        st.session_state.contact_list,
        key=lambda contact:getattr(contact, field),
        reverse=not ascending
    )

    return [{
        "Name": contact.name,
        "Phone": contact.phone,
        "Email": contact.email,
        "Category": contact.category,
        "Favorite": "Yes" if contact.favorite else "No"
    } for contact in sorted_contacts]

def import_contacts(file):
    try:
        if file.endswith(".csv"):
            df = pd.read_csv(f"{file}.csv")
        elif file.endswith(".json"):
            df = json.loads(f"{file}.json")
        else:
            return "Invalid file format"

        success_count = 0
        for _, row in df.iterrows():
            try:
                favorite_val = row.get('Favorite', False)
                if isinstance(favorite_val, str):
                    favorite_val = (favorite_val.lower() == 'yes' or favorite_val.lower() == 'true')

                contact = Contact(row['Name'], row['Phone'], row['Email'], 
                                  category=row.get('Category', 'General'),
                                  favorite=favorite_val)
                st.session_state.contact_list.append(contact)
                success_count += 1
            except ValueError as e:
                st.warning(f"Skipping Invalid contact: {e}")

        return f"Loaded {success_count} contacts from {file}.csv"
    except Exception as e:
        return f"Error loading file: {e}"
    
def export_contacts(format_type, filename):
    filename = st.text_input("Filename", placeholder="Please input a filename")
    if not filename:
        return "Please provide a valid filename to export to"

      
    contact_data = []
    for contact in st.session_state.contact_list:
        contact_data.append({
            "Name": contact.name,
            "Phone": contact.phone,
            "Email": contact.email,
            "Category": contact.category,
            "Favorite": contact.favorite
        })
    contact_df = pd.DataFrame(contact_data)

    try:
        if format_type == ".csv":
            contact_df.to_csv(f"{filename}.csv", index=False)
            return f"Contacts exported to {filename}.csv successfully"
        elif format_type == ".json":
            contact_df.to_json(f"{filename}", index=False)
            return f"Contacts exported to {filename}.json successfully"
        else:
            return "Unsupported format type"
        
    except Exception as e:
        return f"Error saving file: {e}"

# Filter by category
def filter_by_category(category):
    if not category:
        return []
    
    category_data = []

    for contact in st.session_state.contact_list:
        if contact.category == category:
            category_data.append({
                "Name": contact.name,
                "Phone": contact.phone,
                "Email": contact.email,
                "Favorite": "Yes" if contact.favorite else "No"
            })
    return category_data
    
# Main application
def Contacts_App():
    st.header("Contact List")

    st.sidebar.title("Contact list Functions")
    st.header("Navigation")
    function_option = st.sidebar.selectbox(
            "Contact List Functions",
            ["Add Contact", "View Contact", "Search Contact", "Edit Contact", 
             "File Operations", "Sort Contacts", "View Category", "View Favorite",
             "Contact Cards"]
        )

    if function_option == "Add Contact":
        st.title("Add New Contact")

        with st.form("Add New Contact"):
            name = st.text_input("Please input name")
            phone = st.text_input("Please input phone number in the following format (+123xxxxxxxxxx)")
            email = st.text_input("Please input your email")
            category = st.selectbox("Category", options=st.session_state.category)
            favorite = st.checkbox("Add to Favorites")
    
            if st.form_submit_button("Add contact"):
                if name and phone and email:
                    duplicate = False
                    for contact in st.session_state.contact_list:
                        if name == contact.name and phone == contact.phone and email == contact.email:
                            duplicate = True
                            break
                    if not duplicate:
                        try:
                            new_contact = Contact(name, phone, email, category, favorite)
                            add_contact(new_contact)
                            st.success(f"Contact {name} has been added to the list")
            
                            # Save File if name exists
                            if st.session_state.filename:
                                    
                                filename = st.session_state.filename[-1]
                                save_contacts_to_file(filename)
                                st.success("Autosave successful")

                        except ValueError as e:
                            st.error(f"Error: {e}")
                    else:
                        st.error("Contact already exists")
        
            else:
                st.error(f"Please input the correct details")
        

    # View Contacts
    elif function_option == "View Contact":
        st.title("View Contacts")

        if st.session_state.contact_list:
            contacts_df = pd.DataFrame(view_all_contacts())

            st.dataframe(contacts_df)

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Save Contacts"):
                    filename = st.text_input("Input filename")
                    if filename:
                        result = save_contacts_to_file(filename)
                        st.session_state.filename.append(filename)
                        st.success(result)

            with col2:
                #Add delete here
                contact_indices = [f"{i}: {contact.name}" for i, contact in enumerate(st.session_state.contact_list)]
                if contact_indices:
                    select_to_delete = st.selectbox("Select contact to delete:" ,options=contact_indices)
                    if st.button("Delete Selected Contact"):
                        index = int(select_to_delete.split(":")[0])
                        confirm = st.checkbox("Confirm deletion")
                        if confirm:
                            result = delete_contact(index)
                            st.success(result)
        else:
             st.info("No contacts yet. Add some contacts")
            
    # Search Contacts
    elif function_option == "Search Contact":
        st.title("Search Contact")

        query = st.text_input("Input your search item")

        search_results = search_contact(query)

        if query:
            if search_results:
                search_df = pd.DataFrame(search_contact(query))
                st.dataframe(search_df)

                contact_indices = []
                for i, result in enumerate(search_results):
                    for j, contact in enumerate(st.session_state.contact_list):
                        if (result["Name"] == contact.name and
                            result["Phone"] == contact.phone and
                            result["Email"] == contact.email):
                            contact_indices.append((j, contact.name))
                
                if contact_indices:
                    selected = st.selectbox("Select a contact to delete:", 
                                            [f"{i}: {name}" for i, name in contact_indices]
                                            )
                    if st.button("Delete Contact"):
                        index = int(selected.strip(":")[0])
                        confirm = st.checkbox("Confirm Delete")
                        if confirm:
                            result = delete_contact(index)
                            st.success(result)
            else:
                st.info("No matching contacts found")
        else:
            st.info("Enter a search term above")
 

    #Editing contacts
    elif function_option == "Edit Contact":
        st.title("Edit Contacts")

        if not st.session_state.contact_list:
            st.info("No contacts to edit. Please add contacts")
        else:

            contacts_df = pd.DataFrame(view_all_contacts())

            st.dataframe(contacts_df)
            contact_indices = [f"{i}: {contact.name}" for i, contact in enumerate(st.session_state.contact_list)]
            selected_contact = st.selectbox("Select a contact to edit:", contact_indices)
                
            # Getting index from the selection
            if selected_contact:
                index = int(selected_contact.split(":")[0])
                contact = st.session_state.contact_list[index]

                # Creating the edit form
                with st.form("Edit Contact"):
                    
                    edit_name = st.text_input("Please input the name", value=contact.name)
                    edit_phone = st.text_input("Please input the number", value=contact.phone)
                    edit_email = st.text_input("Please input the email", value=contact.email)
                    edit_category = st.selectbox("Please input the category",
                                                 options=st.session_state.category,
                                                 index=st.session_state.category.index(contact.category)
                                                    if contact.category in st.session_state.category else 0)
                    edit_favorite = st.checkbox("Favorite", value=contact.favorite)


                if st.form_submit_button("Edit"):
                    try:
                        if not edit_name or not edit_phone or not edit_email:
                            st.error("All fields are required")
                        else:
                            
                            result = update_contact(index, edit_name, edit_phone, edit_email, edit_category, edit_favorite)
                            st.success(result)

                            if st.session_state.filename:
                                filename = st.session_state.filename[-1]
                                save_contacts_to_file(filename)
                                st.success(f"Contacts saved to {filename}.csv")
                    except ValueError as e:
                        st.error(f"Error: {e}")

    # File Operations         
    elif function_option == "File Operations":
        st.title("File Operations")

        tab1, tab2, tab3, tab4 = st.tabs(["Save", "Load", "Import", "Export"])

        with tab1:
            st.header("Save Contacts")
            filename - st.text_input("Please enter ilename to save")
            if st.button("Save to file"):
                if filename:
                    results = save_contacts_to_file(filename)
                    if "Error" not in result:
                        st.session_state.filename.append(filename)
                    st.success(result)
                else:
                    st.error("Please enter a filename")

        with tab2:
            st.header("Load Contacts")
            load_filename = st.tect_input("Enter filename to load")

            if st.button("Load from file"):
                if load_filename:
                    result = load_contact_from_file(load_filename)
                    st.info(result)
                else:
                    st.error("Please enter a filename")
                
        with tab3:
            st.header("Import Contacts")
            uploaded_file =st.file_upload("Upload CSV or JSON file", type=["csv", "json"])
            if uploaded_file is not None:
                if st.button("Import"):
                    result = import_contacts(uploaded_file)
                    st.info(result)

        with tab4:
            st.header("Export Contacts")
            export_filename = st.text_input("Enter filename for export")
            export_format = st.radio("Select format", ["csv", "json"])
            if st.button("Export"):
                if export_filename:
                    result = export_contacts(export_format, export_filename)
                    st.success(result)
                else:
                    st.error("Please enter a filename")

    # Sort Contacts
    elif function_option == "Sort Contacts":
        st.title("Sort Contacts")

        if not st.session_state.contact_list:
            st.info("No contacts to sort. Please add contacts")
        else:
            sort_field = st.selectbox("Sort By", options=list ,placeholder="Select Column(s) to sort by")
            ascending = st.checkbox("Ascending Order", value=True)

            if st.button("Sort"):
                sorted_data = sort_contacts(sort_field, ascending)
                if sorted_data:
                    st.dataframe(pd.DataFrame(sorted_data))
                else:
                    st.info("No contacts to sort")

    # View Category
    elif function_option == "View Category":
        st.title("View Category")

        if not st.session_state.category:
            st.info("No categories available. Please create one")
        else:
            with st.expander("Add new category"):
                new_category = st.text_input("New category name")
                if st.button("Add Category"):
                    if new_category:
                        result = add_category(new_category)
                        st.success(result)
                            
            category = st.session_state.category
            select = st.selectbox("Select Category", options=category, placeholder="Select the Category you'd like to view")

            if st.button("View"):
                category_data = filter_by_category(select)
                if category_data:
                    st.dataframe(pd.DataFrame(category_data))
                else:
                    st.info(f"No contacts in category '{select}'")

    # View Categories
    elif function_option == "View favorite":
        st.title("Favorite Contacts")

        favorites = filter_favorite()

        if favorites:
            favorite = pd.DataFrame(favorites)

            st.dataframe(favorite)
        else:
            st.info("No favorite contacts found")

    #Add favorite
    elif function_option == "Add Favorite":
        st.title("Add favorite")
        if st.session_state.contact_list:
            index_list = [f"{i}: {contact.name} - {contact.phone}" for i, contact in enumerate(st.session_state.contact_list)]

            selected_contact = st.select_box("Favorite", options=index_list, placeholder="Please select the contact")

            if st.button("Add to Favorites"):
                select_index = int(selected_contact.strip(":")[0])
                results = add_to_favorite(select_index)

                st.success(results)

    # Contact cards
    elif function_option == "Contact Cards":
        st.title("Contact cards")
        if not st.session_state.contact_list:
            st.info("No contacts to display. Please add contacts")
        else:

            contacts_per_row = 4

            place_holder = "https://www.nosm.ca/our-community/indigenous-medical-education/indigenous-affairs-office/default-profile-picture-avatar-photo-placeholder-vector-illustration-2/"

            for i in range(0, len(st.session_state.contact_list), contacts_per_row):
                cols = st.columns(contacts_per_row)
                for j in range(contacts_per_row):
                    if i+j < len(st.session_state.contact_list):
                        contact = st.session_state.contact_list[i+j]
                        with cols[j]:
                            with st.container():
                                st.markdown("---")
                                st.image(place_holder, width=100)
                                st.markdown(f"**Name:** {contact.name}")
                                st.markdown(f"**Phone:** {contact.phone}")
                                st.markdown(f"**Email:** {contact.email}")
                                st.markdown(f"**Category:** {contact.category}")
                                if contact.favorite:
                                    st.markdown("⭐ **Favorite**")
                                st.markdown("---")


if __name__ == "__main__":
    Contacts_App()





