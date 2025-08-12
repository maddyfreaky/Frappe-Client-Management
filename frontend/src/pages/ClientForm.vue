<template>
  <div class="container mx-auto px-4 py-8">
    
    <div class="grid grid-cols-1 lg:grid-cols-8 gap-8 mb-8">
      <div class="lg:col-span-8">
        <div class="bg-white p-6 shadow-md rounded-md">
          <h2 class="text-xl font-semibold text-center mb-6">Create Client</h2>
         
          <form @submit.prevent="submitForm" class="space-y-4 sub">
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Client Name*</label>
              <TextInput v-model="form.client_name" required />
            </div>
 
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Select Contact Person*</label>
              <div class="flex">
                <select
                  ref="contactPersonRef"
                  multiple
                  class="w-full rounded-l-md border border-gray-300 text-sm"
                >
                  <option v-for="user in users" :key="user.name" :value="user.name">
                    {{ user.full_name || user.name }}
                  </option>
                </select>
                <!-- <button
                  type="button"
                  @click="handleAddContactPerson"
                  class="bg-black text-white px-3 py-1 rounded-r-md hover:bg-gray-800"
                >
                  +
                </button> -->
              </div>
            </div>
 
           
            <div v-if="fetchedContactInfo.length" class="space-y-3">
              <div
                v-for="(info, idx) in fetchedContactInfo"
                :key="idx"
                class="grid grid-cols-1 md:grid-cols-3 gap-4 bg-gray-100 p-3 rounded border border-gray-200"
              >
                <TextInput :modelValue="info.full_name" label="Name" readonly />
                <TextInput v-model="info.email" label="Email" />
              </div>
            </div>
 
         
 
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Selected Users*</label>
              <select
                ref="selectedUsersRef"
                multiple
                class="w-full rounded-md border border-gray-300 text-sm"
              >
                <option v-for="user in users" :key="user.name" :value="user.name">
                  {{ user.full_name || user.name }}
                </option>
              </select>
            </div>
 
            
        <div class="pt-4">
  <button type="submit" class="bg-black text-white px-2 py-2 text-sm rounded">
    Submit
  </button>
</div>
 
            
            <Alert
              v-if="message"
              :variant="status === 'success' ? 'green' : 'red'"
              class="mt-4"
            >
              {{ message }}
            </Alert>
          </form>
        </div>
      </div>
    </div>
 
   
    <div class="grid grid-cols-1 lg:grid-cols-8 gap-8">
      <div class="lg:col-span-8">
        <div class="bg-white p-6 shadow-md rounded-md">
         
          <div class="overflow-x-auto">
            <table class="min-w-full bg-white border border-gray-200 rounded-lg">
              <thead class="bg-gray-100">
                <tr>
                  <th class="py-3 px-4 border-b text-left w-10">
                    <input
                      type="checkbox"
                      v-model="selectAll"
                      @change="toggleSelectAll"
                      class="h-4 w-4 text-blue-600 rounded focus:ring-blue-500 border-gray-300"
                    >
                  </th>
                  <th class="py-3 px-4 border-b text-left">Client Name</th>
                  <th class="py-3 px-4 border-b text-left">Created At</th>
                  <th class="py-3 px-4 border-b text-left">Created By</th>
                  <th class="py-3 px-4 border-b text-left w-32">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="client in paginatedClients" :key="client.name" class="hover:bg-gray-50">
                  <td class="py-3 px-4 border-b">
                    <input
                      type="checkbox"
                      v-model="selectedClients"
                      :value="client.name"
                      class="h-4 w-4 text-blue-600 rounded focus:ring-blue-500 border-gray-300"
                    >
                  </td>
                  <td class="py-3 px-4 border-b">{{ client.client_name }}</td>
                  <td class="py-3 px-4 border-b">{{ client.created_at }}</td>
                  <td class="py-3 px-4 border-b">{{ client.created_by }}</td>
                  <td class="py-3 px-4 border-b">
                    <div class="flex space-x-2">
                      
                      <button
                        @click="viewClient(client)"
                        class="text-dark-500 hover:text-dark-700 p-1 rounded hover:bg-dark-50"
                        title="View"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      </button>
                     
                      
                <button
  @click="editClient(client)"
  class="text-dark-500 hover:text-dark-700 p-1 rounded hover:bg-dark-50"
  title="Edit"
>
  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
  </svg>
</button>
 
                     
                     
                      <button
    @click="confirmDelete(client)"
    class="text-dark-500 hover:text-dark-700 p-1 rounded hover:bg-dark-50"
    title="Delete"
  >
    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
  </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="clients.length === 0">
                  <td colspan="5" class="py-4 px-4 text-center text-gray-500">No clients found</td>
                </tr>
              </tbody>
            </table>
 
            
            <div v-if="selectedClients.length > 0" class="mt-4 p-3 bg-blue-50 rounded-lg">
              <div class="flex items-center justify-between">
                <span class="text-sm text-blue-700">
                  {{ selectedClients.length }} item(s) selected
                </span>
                <button
                  @click="handleBulkAction"
                  class="px-3 py-1 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
                >
                  Bulk Action
                </button>
              </div>
            </div>
 
            <!-- Pagination -->
            <div class="flex items-center justify-between mt-4">
              <div class="text-sm text-gray-500">
                Showing {{ startItem }} to {{ endItem }} of {{ clients.length }} entries
              </div>
              <div class="flex space-x-2">
                <button
                  @click="prevPage"
                  :disabled="currentPage === 1"
                  class="px-3 py-1 border rounded-md text-sm"
                  :class="{'opacity-50 cursor-not-allowed': currentPage === 1}"
                >
                  Previous
                </button>
                <button
                  @click="nextPage"
                  :disabled="currentPage === totalPages"
                  class="px-3 py-1 border rounded-md text-sm"
                  :class="{'opacity-50 cursor-not-allowed': currentPage === totalPages}"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
 
 
  
<div v-if="viewModalVisible" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
  <div class="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-auto">
    <h2 class="text-xl font-bold mb-4">Client Details</h2>
   
    <div class="mb-6">
      <h3 class="font-semibold text-lg mb-2">Client Information</h3>
      <p><span class="font-medium">Name:</span> {{ viewedClient.client_name }}</p>
      <p><span class="font-medium">Created At:</span> {{ formatDate(viewedClient.created_at) }}</p>
      <p><span class="font-medium">Created By:</span> {{ viewedClient.created_by }}</p>
    </div>
   
    <div class="mb-6">
      <h3 class="font-semibold text-lg mb-2">Contact Persons</h3>
      <div v-if="viewedClient.contact_persons?.length" class="space-y-4">
        <div v-for="person in viewedClient.contact_persons" :key="person.name" class="border p-3 rounded">
          <p><span class="font-medium">Name:</span> {{ person.full_name }}</p>
          <p><span class="font-medium">Email:</span> {{ person.email }}</p>
          <p><span class="font-medium">Mobile:</span> {{ person.mobile_no || 'Not specified' }}</p>
          <p><span class="font-medium">Gender:</span> {{ person.gender || 'Not specified' }}</p>
          <p><span class="font-medium">Bio:</span> {{ person.bio || 'Not specified' }}</p>
        </div>
      </div>
      <p v-else>No contact persons</p>
    </div>
   
    <div class="mb-6">
      <h3 class="font-semibold text-lg mb-2">Selected Users</h3>
      <div v-if="viewedClient.selected_users?.length" class="space-y-4">
        <div v-for="user in viewedClient.selected_users" :key="user.name" class="border p-3 rounded">
          <p><span class="font-medium">Name:</span> {{ user.full_name }}</p>
          <p><span class="font-medium">Email:</span> {{ user.email }}</p>
          <p><span class="font-medium">Mobile:</span> {{ user.mobile_no || 'Not specified' }}</p>
          <p><span class="font-medium">Gender:</span> {{ user.gender || 'Not specified' }}</p>
          <p><span class="font-medium">Bio:</span> {{ user.bio || 'Not specified' }}</p>
        </div>
      </div>
      <p v-else>No selected users</p>
    </div>
   
    <button
      @click="viewModalVisible = false"
      class="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
    >
      Close
    </button>
  </div>
</div>
 
</template>
 
<script setup>
import { ref, reactive, onMounted, nextTick, computed, watch } from 'vue'
import { TextInput, Button, Alert } from 'frappe-ui'
import { useRouter } from 'vue-router' 
 
 
const users = ref([])
const fetchedContactInfo = ref([])
const clients = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const selectedClients = ref([])
const selectAll = ref(false)
const router = useRouter() 
 
 
const form = reactive({
  client_name: '',
  contact_person: [],
  selected_users: [],
})
 
const message = ref('')
const status = ref('')
 
const contactPersonRef = ref(null)
const selectedUsersRef = ref(null)
 
 

const formatDate = (dateString) => {
  if (!dateString) return 'Unknown date'
 
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return dateString 
   
    const day = String(date.getDate()).padStart(2, '0')
    const month = String(date.getMonth() + 1).padStart(2, '0') 
    const year = date.getFullYear()
   
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
   
    return `${day}-${month}-${year} ${hours}:${minutes}:${seconds}`
  } catch (error) {
    console.error('Error formatting date:', error)
    return dateString 
  }
}
 
 
 

const totalPages = computed(() => Math.ceil(clients.value.length / pageSize.value))
const startItem = computed(() => (currentPage.value - 1) * pageSize.value + 1)
const endItem = computed(() => Math.min(currentPage.value * pageSize.value, clients.value.length))
const paginatedClients = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return clients.value.slice(start, end)
})
const viewClient = async (client) => {
  try {
    const response = await fetch(
      `/api/method/client_management.client_management.doctype.clientformdata.clientformdata.get_client_details?name=${encodeURIComponent(client.name)}`
    );
   
    if (!response.ok) throw new Error('Failed to fetch client details');
   
    const result = await response.json();
    if (!result.message) throw new Error('Client data not found');
   
    const clientData = result.message;
   
    
    let contactPersonsDetails = 'None';
    if (clientData.contact_persons && clientData.contact_persons.length > 0) {
      contactPersonsDetails = clientData.contact_persons.map(person => `
        - Name: ${person.full_name}
        Email: ${person.email}
        Mobile: ${person.mobile_no || 'Not specified'}
        Gender: ${person.gender || 'Not specified'}
        Bio: ${person.bio}
      `).join('\n\n');
    }
   
    
    let selectedUsersDetails = 'None';
    if (clientData.selected_users && clientData.selected_users.length > 0) {
      selectedUsersDetails = clientData.selected_users.map(user => `
        - Name: ${user.full_name}
        Email: ${user.email}
        Mobile: ${user.mobile_no || 'Not specified'}
        Gender: ${user.gender || 'Not specified'}
        Bio: ${user.bio}
      `).join('\n\n');
    }
   
    
    const alertMessage = `
      CLIENT DETAILS
      ==============
      Client Name: ${clientData.client_name || 'Not available'}
     
      CONTACT PERSONS:
      ${contactPersonsDetails}
     
      SELECTED USERS:
      ${selectedUsersDetails}
     
      Created At: ${clientData.created_at ? new Date(clientData.created_at).toLocaleString() : 'Unknown date'}
      Created By: ${clientData.created_by || 'Unknown'}
    `;
   
    
    alert(alertMessage);
   
  } catch (error) {
    console.error('Error viewing client:', error);
    alert('Error loading client details: ' + error.message);
  }
};
const editClient = (client) => {
  
  router.push({
    name: 'EditClientFile',
    params: { name: client.name }
  })
}
 
const confirmDelete = (client) => {
  if (confirm(`Are you sure you want to permanently delete ${client.client_name}? This action cannot be undone.`)) {
    deleteClient(client)
  }
}
const deleteClient = async (client) => {
  try {
    const response = await fetch(`/api/resource/ClientFormData/${client.name}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.frappe?.csrf_token || ''
      }
    });
 
    const result = await response.json();
 
    if (response.ok) {
      
      clients.value = clients.value.filter(c => c.name !== client.name);
      selectedClients.value = selectedClients.value.filter(name => name !== client.name);
 
      
      const totalRemaining = clients.value.length;
      const newTotalPages = Math.ceil(totalRemaining / pageSize.value);
      if (currentPage.value > newTotalPages) {
        currentPage.value = newTotalPages || 1;
      }
 
      
      if (typeof frappe !== 'undefined' && frappe.show_alert) {
        frappe.show_alert({
          message: (typeof __ === 'function' ? __('Data deleted successfully') : 'Data deleted successfully'),
          indicator: 'green'
        }, 5);
      } else {
        alert('Data deleted successfully'); // fallback if frappe not loaded
      }
 
    } else {
      throw new Error(result.message || 'Failed to delete client');
    }
 
  } catch (error) {
    console.error('Delete failed:', error);
 
    
    if (typeof frappe !== 'undefined' && frappe.show_alert) {
      frappe.show_alert({
        message: (typeof __ === 'function' ? __('Error: ') : 'Error: ') + error.message,
        indicator: 'red'
      }, 5);
    } else {
      alert('Error: ' + error.message); 
    }
  }
};
 
 

const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedClients.value = paginatedClients.value.map(client => client.name)
  } else {
    selectedClients.value = []
  }
}
 
const handleBulkAction = () => {
  alert(`Performing action on selected clients: ${selectedClients.value.join(', ')}`)
}
 

watch(selectedClients, (newVal) => {
  selectAll.value = newVal.length === paginatedClients.value.length && paginatedClients.value.length > 0
}, { deep: true })
 
const initializeSelect2 = (element, formField) => {
  $(element).select2({
    width: '100%',
    placeholder: 'Select options',
    allowClear: true
  }).on('change', (e) => {
    form[formField] = $(e.target).val()
  })
}
 
const fetchUsers = async () => {
  try {
    const res = await fetch('/api/method/client_management.api.user.get_users')
    const json = await res.json()
    users.value = json.message || []
 
    await nextTick()
    initializeSelect2(contactPersonRef.value, 'contact_person')
    initializeSelect2(selectedUsersRef.value, 'selected_users')
  } catch (error) {
    console.error('Error fetching users:', error)
    message.value = 'Failed to load users'
    status.value = 'error'
  }
}
 
const fetchClients = async () => {
  try {
    const res = await fetch('/api/method/client_management.client_management.doctype.clientformdata.clientformdata.get_all_clients')
    const json = await res.json()
    clients.value = (json.message || []).map(client => ({
      ...client,
      created_at: formatDate(client.creation || client.created_at), // Format the date here
      emails: client.contact_person ? client.contact_person.map(p => `${p}@example.com`) : [],
    }))
    currentPage.value = 1
    selectedClients.value = []
  } catch (error) {
    console.error('Error fetching clients:', error)
    message.value = 'Failed to load clients'
    status.value = 'error'
  }
}
 
const handleAddContactPerson = async () => {
  fetchedContactInfo.value = form.contact_person.map((name) => {
    const user = users.value.find((u) => u.name === name)
    return {
      full_name: user?.full_name || user?.name,
      email: `${user?.name}`,
 
     
     
    }
  })
}
 
const submitForm = async () => {
  const payload = {
    client_name: form.client_name,
    contact_person: form.contact_person,
    selected_users: form.selected_users,
  }
 
  try {
    const response = await fetch(
      '/api/method/client_management.client_management.doctype.clientformdata.clientformdata.save_client_form',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.frappe?.csrf_token || ''
        },
        body: JSON.stringify({ data: JSON.stringify(payload) })
      }
    )
 
    const result = await response.json()
    status.value = result.status
    message.value = result.message
 
    if (status.value === 'success') {
      if (window.frappe?.show_alert) {
        window.frappe.show_alert({ message: result.message, indicator: 'green' }, 3)
      }
 
      
      form.client_name = ''
      form.contact_person = []
      form.selected_users = []
      fetchedContactInfo.value = []
 
      // Reset Select2 fields
      $(contactPersonRef.value).val(null).trigger('change')
      $(selectedUsersRef.value).val(null).trigger('change')
 
      await fetchClients()
    }
  } catch (error) {
    status.value = 'error'
    message.value = 'An error occurred while submitting the form: ' + error.message
  }
}
 
// Pagination controls
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    selectedClients.value = []
  }
}
 
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    selectedClients.value = []
  }
}
 
onMounted(async () => {
  await fetchUsers()
  await fetchClients()
})
</script>
 
<style scoped>
/* Custom styles for Select2 */
.select2-container {
  width: 100% !important;
  min-height: 38px;
}
 
.select2-selection {
  border: 1px solid #d1d5db !important;
  border-radius: 0.375rem !important;
  min-height: 38px !important;
}
 
.select2-selection--multiple {
  padding-top: 2px !important;
  padding-bottom: 2px !important;
}
 
.select2-search__field {
  margin-top: 0 !important;
}
 
/* Table styles */
table {
  border-collapse: separate;
  border-spacing: 0;
  font-size: 13px;
}
 
th {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
}
 
td, th {
  vertical-align: middle;
}
 
tr:last-child td {
  border-bottom: none;
}
 
/* Pagination styles */
button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
 
/* Checkbox styles */
input[type="checkbox"] {
  cursor: pointer;
}
 
/* Action button styles */
.action-button {
  transition: all 0.2s ease;
}
 
.action-button:hover {
  transform: scale(1.1);
}
</style>
 