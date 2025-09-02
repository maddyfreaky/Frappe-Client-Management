# Copyright (c) 2025, Manoj and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class ClientFormData(Document):
	pass

import frappe
import json
import frappe
import json
from frappe import _
 
@frappe.whitelist()
def save_client_form(data):
    # try:
        data = json.loads(data)
       
        # Validate required fields
        if not data.get("client_name"):
            frappe.throw("Client Name is required")
        if not data.get("contact_person"):
            frappe.throw("At least one Contact Person is required")
        if not data.get("selected_users"):
            frappe.throw("At least one User must be selected")
 
        # Create new document
        doc = frappe.new_doc("ClientFormData")
        doc.client_name = data.get("client_name")
 
        # Add contact persons
        for person in data.get("contact_person", []):
            if not person.get("user"):
                continue  # Skip if no user specified
           
            doc.append("contact_person", {
                "user": person.get("user"),
                "email": person.get("email"),
                "full_name": person.get("full_name")
            })
 
        # Add selected users
        for user in data.get("selected_users", []):
            doc.append("selected_users", {"user": user})
 
        doc.insert()
        frappe.db.commit()
 
        return {"status": "success", "message": "Client saved successfully"}
 
    # except Exception as e:
    #     frappe.log_error(frappe.get_traceback(), "ClientForm Save Error")

        # return {"status": "error", "message": str(e)}
    

@frappe.whitelist()
def get_all_clients():
    clients = frappe.get_all(
        "ClientFormData",
        fields=["name", "client_name", "creation", "owner"]
    )
    for client in clients:
        client["created_at"] = frappe.utils.format_datetime(client["creation"], "dd-mm-yyyy hh:mm:ss")
        client["created_by"] = frappe.get_value("User", client["owner"], "full_name") or client["owner"]
    return clients
 
 
@frappe.whitelist()
def get_client_details(name):
    try:
        if not name:
            frappe.throw("Client name is required")
           
        client = frappe.get_doc("ClientFormData", name)
       
        
        contact_persons = []
        if client.contact_person:  # Make sure this matches your DocType field name
            if isinstance(client.contact_person, str):
                contact_person_names = [p.strip() for p in client.contact_person.split(",")] if client.contact_person else []
            else:
                contact_person_names = client.contact_person
               
            for user_name in contact_person_names:
                user_details = frappe.get_doc("User", user_name)
                contact_persons.append({
                    "name": user_name,
                    "full_name": user_details.full_name,
                    "email": user_details.email,
                    "mobile_no": user_details.mobile_no,
                    "gender": user_details.gender,
                    "bio": user_details.bio or "Not specified"
                })
       
        
        selected_users = []
        if hasattr(client, "selected_users"):
            for row in client.selected_users:
                user_details = frappe.get_doc("User", row.user)
                selected_users.append({
                    "name": row.user,
                    "full_name": user_details.full_name,
                    "email": user_details.email,
                    "mobile_no": user_details.mobile_no,
                    "gender": user_details.gender,
                    "bio": user_details.bio or "Not specified"
                })
       
        return {
            "client_name": client.client_name,
            "contact_persons": contact_persons,  
            "selected_users": selected_users,
            "created_at": client.creation,
            "created_by": client.owner
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Client Details Error")
        frappe.throw("Failed to get client details")

@frappe.whitelist()
def get_edit_client_details(name):
    try:
        if not name:
            frappe.throw("Client name is required")
           
        client = frappe.get_doc("ClientFormData", name)
       
        # Get contact persons - handle as table field
        contact_persons = []
        if hasattr(client, "contact_name") and isinstance(client.contact_name, list):
            for row in client.contact_name:
                try:
                    user = frappe.get_doc("User", row.user)
                    contact_persons.append({
                        "name": user.name,
                        "full_name": user.full_name,
                        "email": user.email,
                        "mobile_no": user.mobile_no
                    })
                except Exception as e:
                    frappe.log_error(f"Error loading contact user {row.user}")
                    continue
       
        # Get selected users
        selected_users = []
        if hasattr(client, "selected_users"):
            for row in client.selected_users:
                try:
                    user = frappe.get_doc("User", row.user)
                    selected_users.append({
                        "name": user.name,
                        "full_name": user.full_name,
                        "email": user.email,
                        "mobile_no": user.mobile_no
                    })
                except Exception as e:
                    frappe.log_error(f"Error loading selected user {row.user}")
                    continue
       
        return {
            "client_name": client.client_name,
            "contact_persons": contact_persons,
            "selected_users": selected_users,
            "created_at": client.creation,
            "created_by": client.owner
        }
       
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Client Details Error")
        frappe.throw("Failed to get client details")
 
@frappe.whitelist()
def update_client(name, data):
    try:
        doc = frappe.get_doc("ClientFormData", name)
       
        # Update basic fields
        doc.client_name = data.get("client_name", doc.client_name)
       
        # Update contact_name table
        doc.contact_name = []  # Clear existing contacts
        for user in data.get("contact_person", []):
            doc.append("contact_name", {
                "user": user
            })
       
        # Update selected_users table
        doc.selected_users = []  # Clear existing users
        for user in data.get("selected_users", []):
            doc.append("selected_users", {
                "user": user
            })
       
        doc.save()
        frappe.db.commit()
       
        return "success"
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Client Update Error")
        frappe.throw("Failed to update client")

@frappe.whitelist()
def get_users():
    return frappe.get_all("User",
        filters={
            "enabled": 1,
            "role_profile_name": "Client"  # Filter for users with Client role profile
        },
        fields=["name", "full_name", "mobile_no"]
    )