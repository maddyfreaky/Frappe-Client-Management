import frappe
from frappe.utils import nowdate, getdate, add_days, formatdate
from datetime import datetime

@frappe.whitelist()
def recreate_recurring_activities():
    """
    Scheduled job to recreate recurring activities on their scheduled day
    Runs daily at 8:30 AM
    """
    today = getdate(nowdate())
    day_of_month = today.day
    
    # Get all recurring activities where recurring_day matches today
    recurring_activities = frappe.get_all("Activity",
        filters={
            "is_recurring": 1,
            "recurring_day": day_of_month,
        },
        fields=["name", "activity_name", "client", "recurring_day", "owner"]
    )
    
    for activity in recurring_activities:
        try:
            # Get the original activity with all tasks
            original_activity = frappe.get_doc("Activity", activity.name)
            
            # Create new activity name with current month and year
            current_month_year = datetime.now().strftime("%B %Y")
            new_activity_name = f"{original_activity.activity_name} - {current_month_year}"
            
            # Check if this month's activity already exists
            if frappe.db.exists("Activity", {"activity_name": new_activity_name}):
                continue
            
            # Create new activity
            new_activity = frappe.new_doc("Activity")
            new_activity.update({
                "activity_name": new_activity_name,
                "client": original_activity.client,
                "is_recurring": 0,
                "recurring_day": 0,
                "owner": original_activity.owner
            })
            
            # Map to store old and new task references for parent-child relationships
            task_map = {}
            
            # Copy all tasks
            for task in original_activity.tasks:
                new_task = frappe.new_doc("Activity Tasks")
                new_task.update({
                    "task_name": task.task_name,
                    "task_type": task.task_type,
                    "from_date": task.from_date,
                    "to_date": task.to_date,
                    "complete_within_days": task.complete_within_days,
                    "description": task.description,
                    "assigned_to": task.assigned_to,
                    "priority": task.priority,
                    "client": original_activity.client,
                    "hide_to_client": task.hide_to_client,
                    "idx": task.idx
                })
                new_activity.append("tasks", new_task)
                task_map[task.name] = new_task
            
            # Insert the new activity
            new_activity.insert(ignore_permissions=True)
            
            # Set parent-child relationships
            for task in original_activity.tasks:
                if task.parent_task:
                    if task.parent_task in task_map:
                        new_task = task_map[task.name]
                        new_task.parent_task = task_map[task.parent_task].name
                        new_task.save()
            
            # Send emails for each task
            send_task_assignment_emails(new_activity)
            
            frappe.db.commit()
            frappe.logger().info(f"Successfully recreated recurring activity: {new_activity_name}")
            
        except Exception as e:
            frappe.log_error(
                title=f"Failed to recreate recurring activity {activity.name}",
                message=frappe.get_traceback()
            )
            frappe.db.rollback()

def send_task_assignment_emails(activity):
    """Send emails for all tasks in the activity"""
    for task in activity.tasks:
        if not task.assigned_to:
            continue
            
        user_email = frappe.db.get_value("User", task.assigned_to, "email")
        if not user_email:
            continue
            
        user_full_name = frappe.db.get_value("User", task.assigned_to, "full_name") or task.assigned_to
        
        if task.parent_task:
            # Child task email
            parent_task = frappe.get_doc("Activity Tasks", task.parent_task)
            subject = f"New Recurring Task Assigned: '{task.task_name}' is Pending with Parent Task"
            message = f"""
            <div style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
                <p>Hi {user_full_name},</p>
                <p>Your recurring task <strong>{task.task_name}</strong> will become active once the parent task <strong>{parent_task.task_name}</strong> is completed.</p>
                
                <h3 style="margin-bottom: 5px;">Task Details:</h3>
                <ul>
                    <li><strong>Activity:</strong> {activity.activity_name}</li>
                    <li><strong>Task Name:</strong> {task.task_name}</li>
                    <li><strong>Description:</strong> {task.description or 'N/A'}</li>
                    <li><strong>Priority:</strong> {task.priority or 'N/A'}</li>
                    <li><strong>Duration:</strong> {task.complete_within_days or 'N/A'} days after parent completion</li>
                </ul>

                <h3 style="margin-bottom: 5px;">Parent Task:</h3>
                <ul>
                    <li><strong>Task Name:</strong> {parent_task.task_name}</li>
                    <li><strong>Description:</strong> {parent_task.description or 'N/A'}</li>
                </ul>

                <br><hr style="border: none; border-top: 1px solid #ccc;">
                <p style="color: #777;">Best regards,<br>Your Team</p>
                <p style="font-size: 12px; color: #999;">This is an auto-generated email. Please do not reply.</p>
            </div>
            """
        else:
            # Independent task email
            subject = f"New Recurring Task Assigned: {task.task_name}"
            message = f"""
            <div style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
                <p>Hi {user_full_name},</p>
                <p>A new recurring task <strong>{task.task_name}</strong> has been assigned to you.</p>

                <h3 style="margin-bottom: 5px;">Task Details:</h3>
                <ul>
                    <li><strong>Activity:</strong> {activity.activity_name}</li>
                    <li><strong>Task Name:</strong> {task.task_name}</li>
                    <li><strong>From Date:</strong> {task.from_date}</li>
                    <li><strong>To Date:</strong> {task.to_date}</li>
                    <li><strong>Priority:</strong> {task.priority or 'N/A'}</li>
                    <li><strong>Description:</strong> {task.description or 'N/A'}</li>
                    <li><strong>Due Days:</strong> {task.complete_within_days or 'N/A'}</li>
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
            delayed=False
        )