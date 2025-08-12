# Copyright (c) 2025, Manoj and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from frappe import _

class Template(Document):
	pass

@frappe.whitelist()
def create_template_with_task(template_name, tasks):
    try:
        
        if not template_name:
            frappe.throw(_("Template Name is required"))
            
        tasks = frappe.parse_json(tasks)
        if not isinstance(tasks, list):
            tasks = [tasks]
            
        if not tasks:
            frappe.throw(_("At least one task is required"))

       
        template = frappe.new_doc("Template")
        template.template_name = template_name

        # Temporary list to store task names before they're created
        task_references = []

        # First pass: Create all tasks without parent references
        for idx, task in enumerate(tasks):
            task_doc = frappe.new_doc("Template Tasks")
            task_doc.update({
                "task_name": task.get("task_name"),
                "task_type": task.get("task_type"),
                "complete_within_days": task.get("complete_within_days"),
                "description": task.get("description", ""),
                "is_child": task.get("is_child", False),
                "parent_task": None,  # Will be set in second pass
                "idx": idx + 1
            })

            if not task.get("is_child"):
                task_doc.from_date = task.get("from_date")
                task_doc.to_date = task.get("to_date")

            # Append to template
            template.append("tasks", task_doc)
            task_references.append(task_doc)

        # Save the template with all tasks
        template.insert(ignore_permissions=True)

        # Second pass: Update parent references
        for idx, task in enumerate(tasks):
            if task.get("is_child") and task.get("parent_index") is not None:
                parent_index = task.get("parent_index")
                if 0 <= parent_index < len(task_references):
                    # Get the child task doc from the template
                    child_task = template.tasks[idx]
                    # Get the parent task's name from our references
                    parent_task_name = task_references[parent_index].name
                    # Update the parent reference
                    child_task.parent_task = parent_task_name
                    # Save this change
                    child_task.db_update()

        # Reload the template to get all changes
        template.reload()

        return {
            "success": True,
            "message": _("Template created successfully with {0} tasks").format(len(tasks)),
            "template_name": template.name
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Template Creation Error")
        return {
            "success": False,
            "message": _("Error: {0}").format(str(e))
        }

@frappe.whitelist()
def update_template_with_task(template_name, new_template_name, tasks):
    try:
       
        if not template_name or not new_template_name:
            frappe.throw(_("Template Name is required"))
            
        tasks = frappe.parse_json(tasks)
        if not isinstance(tasks, list):
            tasks = [tasks]
            
        # Get existing template
        template = frappe.get_doc("Template", template_name)
        template.template_name = new_template_name
        
        
        task_name_mapping = {}
        
        # First pass: Create all tasks and build name mapping
        template.tasks = []  # Clear existing tasks
        for idx, task_data in enumerate(tasks):
            task = frappe.new_doc("Template Tasks")
            task.update({
                "task_name": task_data.get("task_name"),
                "task_type": task_data.get("task_type"),
                "complete_within_days": task_data.get("complete_within_days"),
                "description": task_data.get("description", ""),
                "is_child": task_data.get("is_child", False),
                "parent_task": None,  # Temporary - will be updated in second pass
                "idx": idx + 1
            })
            
            if not task_data.get("is_child"):
                task.from_date = task_data.get("from_date")
                task.to_date = task_data.get("to_date")
            
            template.append("tasks", task)
        
        # Save template to generate names for all tasks
        template.save()
        
        # Build mapping of task indices to their generated names
        task_index_to_name = {idx: task.name for idx, task in enumerate(template.tasks)}
        
        # Second pass: Update parent references
        for idx, task_data in enumerate(tasks):
            if task_data.get("is_child") and task_data.get("parent_index") is not None:
                parent_index = task_data.get("parent_index")
                if 0 <= parent_index < len(task_index_to_name):
                    # Get the child task
                    child_task = template.tasks[idx]
                    # Get the parent task's name
                    parent_task_name = task_index_to_name[parent_index]
                    # Update the parent reference
                    child_task.parent_task = parent_task_name
                    child_task.db_update()
        
        # Final save to ensure all changes
        template.save()
        
        return {
            "success": True,
            "message": _("Template updated successfully with {0} tasks").format(len(tasks)),
            "template_name": template.name
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Template Update Error")
        return {
            "success": False,
            "message": _("Error: {0}").format(str(e))
        }