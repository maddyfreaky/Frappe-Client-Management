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
    try:
        data = json.loads(data)
 
        missing_fields = []
        if not data.get("client_name"):
            missing_fields.append("Client Name")
        if not data.get("contact_person"):
            missing_fields.append("Contact Person")
 
        if missing_fields:
            frappe.throw(
                title="Missing Fields",
                msg="Mandatory fields required in ClientFormData:<br><ul>" +
                    "".join(f"<li>{field}</li>" for field in missing_fields) +
                    "</ul>"
            )
 
        doc = frappe.new_doc("ClientFormData")
        doc.client_name = data.get("client_name")
        doc.contact_person = data.get("contact_person")
        print(doc.contact_person)
     
 
        for user in data.get("selected_users", []):
            print("in for", user)
            doc.append("selected_users", {"user": user})
 
        doc.insert()
        frappe.db.commit()
 
        return {"status": "success", "message": "Client saved successfully"}
 
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "ClientForm Save Error")
        return {"status": "error", "message": str(e)}
    

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
       
        # Get full contact person details
        contact_persons = []
        if client.contact_person:
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
       
        # Get full selected user details
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