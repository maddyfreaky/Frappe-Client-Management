<div style="font-family: Arial, sans-serif; font-size: 14px; color: #333;">
    <p>Hello,</p>
    
    <p>This is a reminder that the task <strong>{{ doc.task_name }}</strong> is due today.</p>
    
    <h3 style="margin-bottom: 5px;">Task Details:</h3>
    <ul>
        <li><strong>Task Name:</strong> {{ doc.task_name }}</li>
        <li><strong>Description:</strong> {{ doc.description or 'N/A' }}</li>
        <li><strong>Priority:</strong> {{ doc.priority or 'N/A' }}</li>
        <li><strong>Assigned To:</strong> {{ doc.assigned_to or 'N/A' }}</li>
        <li><strong>Client:</strong> {{ doc.client or 'N/A' }}</li>
    </ul>

    <p>Please complete the task before end of day.</p>
    
    <br><hr style="border: none; border-top: 1px solid #ccc;">
    <p style="color: #777;">Best regards,<br>Your Team</p>
</div>