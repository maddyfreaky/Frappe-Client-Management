import frappe
from frappe import _
 
@frappe.whitelist()
def get_users():
    return frappe.get_all("User", filters={"enabled": 1}, fields=["name", "full_name",'mobile_no'])


@frappe.whitelist()
def get_users_for_assignment():
    print("hello1")
    try:
        
        users = frappe.get_all('User',
            fields=['name', 'full_name'],
            filters=[
                ['name', 'not in', ['Guest', 'Administrator']],
                ['enabled', '=', 1]
            ]
        )
        
        
        client_users = frappe.get_all('Has Role',
            fields=['parent'],
            filters=[['role', '=', 'Client']],
            pluck='parent'
        )
        
        
        internal_users = [u for u in users if u['name'] not in client_users]
        
        return {
            'success': True,
            'internal_users': internal_users,
            'client_users': client_users
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'User Fetch Error')
        return {
            'success': False,
            'message': str(e)
        }
    



@frappe.whitelist()
def get_client_users(client_id):
    print("hello")
    try:
        if not client_id:
            return {'success': False, 'message': 'Client ID required'}
            
        client = frappe.get_doc('ClientFormData', client_id)
        users = []
        
        for row in client.get('selected_users', []):
            user = frappe.get_doc('User', row.user)
            users.append({
                'name': user.name,
                'full_name': user.full_name
            })
        
        return {
            'success': True,
            'users': users
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), 'Client Users Fetch Error')
        return {
            'success': False,
            'message': str(e)
        }
