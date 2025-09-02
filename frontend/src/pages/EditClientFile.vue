<template>
  <div class="container mx-auto px-4 py-8">
    <div class="grid grid-cols-1 lg:grid-cols-8 gap-8">
      <div class="lg:col-span-8">
        <div class="bg-white p-6 shadow-md rounded-md">
          <h2 class="text-xl font-semibold text-center mb-6">Edit Client</h2>
         
          <form @submit.prevent="submitForm" class="space-y-4">
            <!-- Client Name -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Client Name *</label>
              <TextInput v-model="form.client_name" required />
            </div>
 
            <!-- Contact Person -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Select Contact Person *</label>
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
                          </div>
            </div>
 
            <!-- Selected Users -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Select Users *</label>
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
 
            <!-- Submit Button -->
 <div class="pt-4 flex justify-start space-x-2">
  <Button
    type="button"
    label="Cancel"
    class="w-auto px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-800 text-sm"
    @click="handleCancel"
    :disabled="loading"
  />
  <Button
    type="submit"
    label="Update"
    class="w-auto px-4 py-2 text-sm"
    :loading="loading"
  />
</div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>
 
<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { TextInput, Button, createResource } from 'frappe-ui'
import { useRoute, useRouter } from 'vue-router'
 
 
const route = useRoute()
const router = useRouter()
const loading = ref(false)
 
// State
const users = ref([])
const form = reactive({
  client_name: '',
  contact_person: [],
  selected_users: []
})
 
// Refs for select elements
const contactPersonRef = ref(null)
const selectedUsersRef = ref(null)
 
// Fetch client data
const fetchClient = createResource({
  url: 'client_management.client_management.doctype.clientformdata.clientformdata.get_edit_client_details',
  params: { name: route.params.name },
  auto: true,
  onSuccess(data) {
    form.client_name = data.client_name
    form.contact_person = data.contact_persons?.map(p => p.name) || []
    form.selected_users = data.selected_users?.map(u => u.name) || []
    initSelect2()
  },
  onError(error) {
    console.error('Error fetching client:', error)
    router.push({ name: 'ClientList' })
  }
})
 
 
// Fetch all users
const fetchUsers = createResource({
  url: 'client_management.client_management.doctype.clientformdata.clientformdata.get_users',
  auto: true,
  onSuccess(data) {
    users.value = data
    // If client data is already loaded, initialize select2
    if (form.client_name) initSelect2()
  }
})
 
// Initialize Select2 with current selections
const initSelect2 = () => {
  nextTick(() => {
    // Initialize Contact Person Select2
    $(contactPersonRef.value).select2({
      width: '100%',
      placeholder: 'Select contact persons',
      allowClear: true,
      closeOnSelect: false
    }).val(form.contact_person).trigger('change')
 
    // Initialize Users Select2
    $(selectedUsersRef.value).select2({
      width: '100%',
      placeholder: 'Select users',
      allowClear: true,
      closeOnSelect: false
    }).val(form.selected_users).trigger('change')
  })
}
 
// Handle form submission
const submitForm = async () => {
  try {
    loading.value = true
   
    // Get current selections from Select2
    const contactPersons = $(contactPersonRef.value).val() || []
    const selectedUsers = $(selectedUsersRef.value).val() || []
 
    const response = await fetch('/api/method/client_management.client_management.doctype.clientformdata.clientformdata.update_client', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.frappe?.csrf_token || ''
      },
      body: JSON.stringify({
        name: route.params.name,
        data: {
          client_name: form.client_name,
          contact_person: contactPersons,
          selected_users: selectedUsers
        }
      })
    })
 
    if (!response.ok) throw new Error('Failed to update client')
 
    const result = await response.json()
   
    if (result.message && result.message === 'success') {
      // Show success message
      alert("Updated successfully");
     
     
     
      // Redirect to ClientForm after a slight delay to show the message
      setTimeout(() => {
        router.push({ name: 'Client Creation' })
      }, 500)
    } else {
      throw new Error(result.message || 'Update failed')
    }
  } catch (error) {
    console.error('Error updating client:', error)
    window.frappe.show_alert({
      message: 'Error: ' + error.message,
      indicator: 'red'
    }, 5)
  } finally {
    loading.value = false
  }
}
 
 
const handleCancel = () => {
  router.push({ name: 'Client Creation' }) // Make sure this matches your route name
}
 
onMounted(() => {
  // Initialize when both client and users data are loaded
  if (users.value.length && form.client_name) {
    initSelect2()
  }
})
</script>
 
<style>
/* Your existing Select2 styles */
.select2-container--default .select2-selection--multiple {
  border: 1px solid #d1d5db !important;
  border-radius: 0.375rem !important;
  min-height: 38px !important;
}
 
.select2-container--default .select2-selection--multiple .select2-selection__choice {
  background-color: #e5e7eb !important;
  border: 1px solid #d1d5db !important;
  border-radius: 0.25rem !important;
  padding: 0 5px !important;
}
 
.select2-container--default .select2-selection--multiple .select2-selection__choice__remove {
  color: #6b7280 !important;
  margin-right: 3px !important;
}
 
.select2-container--default .select2-search--inline .select2-search__field {
  margin-top: 0 !important;
  padding: 5px !important;
}
</style>
 