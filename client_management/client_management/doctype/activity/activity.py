# Copyright (c) 2025, Manoj and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from frappe import _


class Activity(Document):
	pass

@frappe.whitelist()
def create_activity_from_template(template_name, client, is_recurring, recurring_day, tasks):
    try:
        if not template_name:
            frappe.throw("Template name is required")
        if not client:
            frappe.throw("Client is required")
            
        tasks = frappe.parse_json(tasks)
        if not isinstance(tasks, list):
            frappe.throw("Tasks must be a list")

        activity = frappe.new_doc("Activity")
        activity.update({
            "activity_name": template_name,
            "client": client,
            "is_recurring": 1 if is_recurring else 0,
            "recurring_day": recurring_day if is_recurring else None
        })

        task_references = []
        for idx, task_data in enumerate(tasks):
            task = frappe.new_doc("Activity Tasks")
            task.update({
                "task_name": task_data.get("task_name"),
                "task_type": task_data.get("task_type"),
                "from_date": task_data.get("from_date"),
                "to_date": task_data.get("to_date"),
                "complete_within_days": task_data.get("complete_within_days"),
                "description": task_data.get("description"),
                "assigned_to": task_data.get("assign_to"),
                "priority": task_data.get("priority"),
                "client": client,
                "parent_task": None,
                "hide_to_client": 1 if task_data.get("hide_to_client") else 0,
                "idx": idx + 1
            })
            activity.append("tasks", task)
            task_references.append(task)

        # Insert activity and tasks
        activity.insert(ignore_permissions=True)

        # Second pass: set parent references
        for idx, task_data in enumerate(tasks):
            if task_data.get("is_child") and task_data.get("parent_index") is not None:
                parent_index = task_data.get("parent_index")
                if 0 <= parent_index < len(task_references):
                    child_task = activity.tasks[idx]
                    parent_task = task_references[parent_index]
                    child_task.parent_task = parent_task.name
                    child_task.db_update()

        # Send emails
        for idx, task_data in enumerate(tasks):
            assigned_user = task_data.get("assign_to")
            if not assigned_user:
                continue

            user_email = frappe.db.get_value("User", assigned_user, "email")
            if not user_email:
                continue

            user_full_name = frappe.db.get_value("User", assigned_user, "full_name") or assigned_user
            task_doc = activity.tasks[idx]
            is_child = task_data.get("is_child")
            parent_index = task_data.get("parent_index")

            if is_child and parent_index is not None and 0 <= parent_index < len(task_references):
                parent_task_doc = task_references[parent_index]
                subject = f"New Task Assigned:'{task_doc.task_name}' is Pending with Parent Task"
                message = f"""
                <div style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
                    <p>Hi {user_full_name},</p>
                    <p>Your task <strong>{task_doc.task_name}</strong> will become active once the parent task <strong>{parent_task_doc.task_name}</strong> is completed.</p>
                    
                    <h3 style="margin-bottom: 5px;">Task Details:</h3>
                    <ul>
                        <li><strong>Task Name:</strong> {task_doc.task_name}</li>
                        <li><strong>Description:</strong> {task_doc.description or 'N/A'}</li>
                        <li><strong>Priority:</strong> {task_doc.priority or 'N/A'}</li>
                        <li><strong>Duration:</strong> {task_doc.complete_within_days or 'N/A'} days after parent completion</li>
                    </ul>

                    <h3 style="margin-bottom: 5px;">Parent Task:</h3>
                    <ul>
                        <li><strong>Task Name:</strong> {parent_task_doc.task_name}</li>
                        <li><strong>Description:</strong> {parent_task_doc.description or 'N/A'}</li>
                    </ul>

                    <br><hr style="border: none; border-top: 1px solid #ccc;">
                    <p style="color: #777;">Best regards,<br>Your Team</p>
                    <p style="font-size: 12px; color: #999;">This is an auto-generated email. Please do not reply.</p>
                </div>
                """
            else:
                subject = f"New Task Assigned: {task_doc.task_name}"
                message = f"""
                <div style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
                    <p>Hi {user_full_name},</p>
                    <p>A new task <strong>{task_doc.task_name}</strong> has been assigned to you.</p>

                    <h3 style="margin-bottom: 5px;">Task Details:</h3>
                    <ul>
                        <li><strong>Task Name:</strong> {task_doc.task_name}</li>
                        <li><strong>From Date:</strong> {task_doc.from_date}</li>
                        <li><strong>To Date:</strong> {task_doc.to_date}</li>
                        <li><strong>Priority:</strong> {task_doc.priority or 'N/A'}</li>
                        <li><strong>Description:</strong> {task_doc.description or 'N/A'}</li>
                    </ul>

                    <br><hr style="border: none; border-top: 1px solid #ccc;">
                    <p style="color: #777;">Best regards,<br>Your Team</p>
                    <p style="font-size: 12px; color: #999;">This is an auto-generated email. Please do not reply.</p>
                </div>
                """

            frappe.sendmail(
                recipients=[user_email],
                subject=subject,
                message=message,
                
            )


        return {
            "success": True,
            "message": "Activity created successfully",
            "activity_name": activity.name
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Activity Creation Error")
        return {
            "success": False,
            "message": str(e)
        }

    
@frappe.whitelist()
def get_users_for_assignment():
    try:
        users = frappe.get_all('User',
            fields=['name', 'full_name'],
            filters=[
                ['name', 'not in', ['Guest', 'Administrator']],
                ['enabled', '=', 1]
            ]
        )
        
        client_users = frappe.get_all('User',
            fields=['name','role_profile_name'],
            filters=[['role_profile_name', '=', 'Client']],
            pluck='name'
        )
        
        internal_users = [u for u in users if u['name'] not in client_users]

        
        frappe.response["message"] = {
            'success': True,
            'internal_users': internal_users,
            'client_users': client_users
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'User Fetch Error')
        frappe.response["message"] = {
            'success': False,
            'message': str(e)
        }

    



@frappe.whitelist()
def get_client_users(client_id):
    print("hello")
    print(client_id,"client")
    try:
        if not client_id:
            print("HElldaf")
            return {'success': False, 'message': 'Client ID required'}
        print("before client")   
        client = frappe.get_doc('ClientFormData', client_id)
        print("clientname", client)
        
        users = []
        
        for row in client.get('selected_users', []):
            user = frappe.get_doc('User', row.user)
            print(user, "userss")
            users.append({
                'name': user.name,
                'full_name': user.full_name
            })
        print(users,"users")
        return {
            'success': True,
            'users': users
        }
    except Exception as e:
        print(e, "exception1")
        frappe.log_error(frappe.get_traceback(), 'Client Users Fetch Error')
        return {
            'success': False,
            'message': str(e)
        }


@frappe.whitelist()
def get_user_activities(page=1, page_length=20):
    try:
       
        user = frappe.session.user
        
        # Build query to find activities where current user is assigned to any task
        # Include client_name by joining with the Client doctype
        query = """
            SELECT DISTINCT a.name, a.activity_name, a.is_recurring, a.owner, a.creation, a.client,
                   c.client_name,
                   (SELECT COUNT(*) FROM `tabActivity Tasks` WHERE parent=a.name) as tasks_count
            FROM `tabActivity` a
            JOIN `tabActivity Tasks` t ON t.parent = a.name
            LEFT JOIN `tabClientFormData` c ON a.client = c.name
            WHERE t.assigned_to = %(user)s
            ORDER BY a.creation DESC
            LIMIT %(page_length)s OFFSET %(offset)s
        """
        
        
        page = int(page)
        page_length = int(page_length)
        offset = (page - 1) * page_length
        
        
        activities = frappe.db.sql(query, {
            'user': user,
            'page_length': page_length,
            'offset': offset
        }, as_dict=True)
        
       
        total_count = frappe.db.sql("""
            SELECT COUNT(DISTINCT a.name) as total
            FROM `tabActivity` a
            JOIN `tabActivity Tasks` t ON t.parent = a.name
            WHERE t.assigned_to = %(user)s
        """, {'user': user}, as_dict=True)[0].total
        
        return {
            'success': True,
            'activities': activities,
            'total_count': total_count,
            'total_pages': (total_count + page_length - 1) // page_length
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to fetch user activities")
        return {
            'success': False,
            'message': str(e)
        }

@frappe.whitelist()
def get_activity_tasks(activity_name):
    try:
        # Get current user's role profile
        user_role_profile = frappe.db.get_value("User", frappe.session.user, "role_profile_name")
        
        # Base query
        task_fields = [
            'name', 'task_name', 'task_type', 'assigned_to', 
            'status', 'from_date', 'to_date', 'complete_within_days',
            'description', 'hide_to_client'
        ]
        
        # For clients, add hide_to_client filter
        if user_role_profile == 'Client':
            tasks = frappe.get_all(
                'Activity Tasks',
                filters={
                    'parent': activity_name,
                    'hide_to_client': 0  # Only show non-hidden tasks
                },
                fields=task_fields
            )
        else:
            tasks = frappe.get_all(
                'Activity Tasks',
                filters={'parent': activity_name},
                fields=task_fields
            )

        # Get assigned user names
        user_names = list(set(task['assigned_to'] for task in tasks if task['assigned_to']))
        users = {}
        if user_names:
            users_data = frappe.get_all(
                'User',
                filters={'name': ['in', user_names]},
                fields=['name', 'full_name as full_name']
            )
            users = {user['name']: user['full_name'] for user in users_data}

        # Add assigned user names to tasks
        for task in tasks:
            task['assigned_to_name'] = users.get(task['assigned_to'])

        return {
            'success': True,
            'tasks': tasks
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to fetch activity tasks")
        return {
            'success': False,
            'message': str(e)
        }


@frappe.whitelist()
def get_user_activity_tasks():
    try:
        user = frappe.session.user
        
        tasks = frappe.db.sql("""
            SELECT 
                t.name,
                t.task_name,
                t.parent_task,
                t.status,
                t.priority,
                t.from_date,
                t.to_date,
                t.creation,
                t.description,
                a.activity_name,
                a.name as activity_docname,
                pt.status as parent_status
            FROM `tabActivity Tasks` t
            JOIN `tabActivity` a ON t.parent = a.name
            LEFT JOIN `tabActivity Tasks` pt ON t.parent_task = pt.name AND t.parent = pt.parent
            WHERE t.assigned_to = %(user)s
            ORDER BY t.creation DESC  # Order by task creation date
        """, {'user': user}, as_dict=True)
        
        return {
            'success': True,
            'tasks': tasks
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to fetch user activity tasks")
        return {
            'success': False,
            'message': str(e)
        }

@frappe.whitelist()
def update_activity_task_status(activity_name, task_name, status):
    try:
        activity = frappe.get_doc("Activity", activity_name)
        
        # Find the task in the child table
        task = next((t for t in activity.tasks if t.name == task_name), None)
        if not task:
            return {'success': False, 'message': 'Task not found'}
        
        # Check parent task status if this is a child task
        if task.parent_task:
            parent_task = next((t for t in activity.tasks if t.name == task.parent_task), None)
            if parent_task and parent_task.status != "Completed":
                return {
                    'success': False,
                    'message': "Cannot update status - parent task is not completed"
                }
        
        # Only proceed if status is actually changing
        if task.status != status:
            original_status = task.status
            task.status = status
            
            # Only update dates if changing to Completed and has child tasks
            if status == "Completed":
                completion_date = frappe.utils.nowdate()
                
                # Update all child tasks (without modifying parent task dates)
                for child in activity.tasks:
                    if child.parent_task == task.name:
                        # Set from_date to parent's completion date
                        child.from_date = completion_date
                        
                        # Calculate to_date based on complete_within_days
                        if child.complete_within_days:
                            child.to_date = frappe.utils.add_days(completion_date, child.complete_within_days)
                        
                        # Update modified timestamp
                        child.modified = frappe.utils.now_datetime()
            
            activity.save()
            
            # Trigger notifications if status changed to Completed
            if status == "Completed":
                frappe.enqueue(
                    "client_management.client_management.doctype.activity.activity.notify_child_activity_tasks",
                    activity_name=activity_name,
                    parent_task_name=task_name,
                    queue="short"
                )
        
        return {'success': True}
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Failed to update activity task status")
        return {
            'success': False,
            'message': str(e)
        }

def notify_child_activity_tasks(activity_name, parent_task_name):
    # Get all child tasks in the same activity
    child_tasks = frappe.get_all("Activity Tasks",
        filters={
            "parent": activity_name,
            "parent_task": parent_task_name
        },
        fields=["name", "task_name", "assigned_to", "from_date", "to_date", "priority", "complete_within_days"]
    )
    
    if not child_tasks:
        return
    
    # Get parent task details
    parent_task = frappe.db.get_value("Activity Tasks", 
        {
            "parent": activity_name, 
            "name": parent_task_name
        },
        ["task_name", "to_date as parent_completed_date"],
        as_dict=True
    )
    
    activity = frappe.db.get_value("Activity", activity_name, 
        ["activity_name", "name"], as_dict=True)
    
    for child in child_tasks:
        if not child.assigned_to:
            continue
            
       
        subject = f"Parent Task Completed: {parent_task.task_name}"
        message = f"""
            <p>The parent task '<strong>{parent_task.task_name}</strong>' has been marked as completed.
            Your task '<strong>{child.task_name}</strong>' is now active.</p>
            
            <h4>Parent Task Details:</h4>
            <ul>
                <li>Task Name: {parent_task.task_name}</li>
                <li>Completed On: {parent_task.parent_completed_date.strftime('%Y-%m-%d %H:%M') if parent_task.parent_completed_date else 'Not specified'}</li>
            </ul>
            
            <h4>Your Task Details:</h4>
            <ul>
                <li>Task: {child.task_name}</li>
                <li>From Date: {child.from_date.strftime('%Y-%m-%d') if child.from_date else 'Not specified'}</li>
                <li>To Date: {child.to_date.strftime('%Y-%m-%d') if child.to_date else 'Not specified'}</li>
                <li>Priority: {child.priority}</li>
            </ul>
        """
        
        
        frappe.get_doc({
            "doctype": "Communication",
            "subject": subject,
            "content": message,
            "sent_or_received": "Sent",
            "recipients": child.assigned_to,
            "reference_doctype": "Activity",
            "reference_name": activity.name
        }).insert(ignore_permissions=True)
        
        
        frappe.sendmail(
            recipients=child.assigned_to,
            subject=subject,
            message=message,
            reference_doctype="Activity",
            reference_name=activity.name,
            delayed=False
        )

