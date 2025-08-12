# Copyright (c) 2025, Manoj and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from frappe import _


class ActivityComment(Document):
	pass

@frappe.whitelist(allow_guest=False)
def add_activity_comment():
    try:
        data = frappe.local.form_dict
        attachment = None
        
        
        if frappe.request.files:
            file = frappe.request.files.get('file')
            if file:
                file_content = file.stream.read()
                file_doc = frappe.get_doc({
                    "doctype": "File",
                    "file_name": file.filename,
                    "content": file_content,
                    "attached_to_doctype": "Activity Comment",
                    "attached_to_name": "new_comment",
                    "is_private": 1
                })
                file_doc.insert()
                attachment = file_doc.file_url
        
        
        required_fields = ['activity_name', 'comment_type', 'comment']
        missing_fields = [f for f in required_fields if not data.get(f)]
        if missing_fields:
            frappe.throw(f"Missing required fields: {', '.join(missing_fields)}", frappe.ValidationError)
        
        # Create comment
        doc = frappe.get_doc({
            "doctype": "Activity Comment",
            "activity": data['activity_name'],
            "comment_type": data['comment_type'],
            "comment": data['comment'],
            "comment_by": frappe.session.user,
            "comment_date": frappe.utils.now_datetime(),
            "attachment": attachment
        })
        doc.insert(ignore_permissions=True)
        
       
        user_fullname = frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user.split('@')[0]
        
        return {
            "success": True,
            "message": "Comment added successfully",
            "comment_id": doc.name,
            "attachment_url": attachment,
            "user_fullname": user_fullname,
            "comment_date": doc.comment_date.strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Activity Comment Error")
        return {
            "success": False,
            "message": str(e)
        }

@frappe.whitelist()
def get_activity_comments(activity_name, comment_type=None):
    try:
        # For clients, only show External comments
        if "Client" in frappe.get_roles():
            comment_type = "External"
            
        filters = {"activity": activity_name}
        if comment_type:
            filters["comment_type"] = comment_type
            
        comments = frappe.get_all("Activity Comment",
            filters=filters,
            fields=["name", "comment_type", "comment", "comment_by", 
                  "comment_date", "attachment"],
            order_by="comment_date desc"
        )
        
        # Add full names to comments
        for comment in comments:
            user_fullname = frappe.db.get_value("User", comment.comment_by, "full_name")
            comment["comment_by_fullname"] = user_fullname
        
        return {
            "success": True,
            "comments": comments
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to get comments")
        return {
            "success": False,
            "message": str(e)
        }

@frappe.whitelist()
def is_user_client():
    try:
        # Method 1: Check role profile name
        role_profile = frappe.db.get_value("User", frappe.session.user, "role_profile_name")
        if role_profile == "Client":
            return True
        
        # Method 2: Check if 'Client' role exists in user roles
        user_roles = frappe.get_roles(frappe.session.user)
        return "Client" in user_roles
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error checking user role")
        return False