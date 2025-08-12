<template>
  <div class="max-w-3xl mx-auto p-6">
    
    <div v-if="loading && !formData.template_name" class="text-center py-8">
      Loading template data...
    </div>

    
    <div v-if="errorMessage" class="mb-4 p-4 bg-red-100 text-red-700 rounded-md">
      {{ errorMessage }}
    </div>

    <div v-if="showSuccess" class="mb-4 p-4 bg-green-100 text-green-700 rounded-md">
      Activity created successfully!
    </div>

    
    <div v-if="formData.template_name" class="card">
      <h2 class="card-header">Create Activity from Template</h2>
      <form @submit.prevent="submitForm" class="card-body">
        
        <Input
          label="Activity Name"
          v-model="formData.template_name"
          type="text"
          class="mb-4"
          @blur="validateActivityName"
        />

        
        <div class="grid grid-cols-2 gap-4 mb-6">
          
          <div class="col-span-2">
            <Checkbox
              v-model="formData.is_recurring"
              label="Is Recurring Activity"
              @change="handleRecurringChange"
            />
          </div>

          
          <div v-if="formData.is_recurring" class="col-span-2">
            <Select
              v-model="formData.recurring_day"
              :options="daysOfMonth"
              label="Select day of the month"
              required
            />
          </div>

          
          <div class="col-span-2">
            <Select
              v-model="formData.client"
              :options="clientOptions"
              label="Client"
              required
              @change="handleClientChange($event.target.value)"
            />
          </div>
        </div>

        
        <div v-for="(task, index) in formData.tasks" :key="index" class="card mb-4 relative">
          <div v-if="index > 0" class="absolute top-2 right-2">
            <Button @click="removeTask(index)" variant="ghost" size="sm">
              Remove
            </Button>
          </div>
          
          <h3 class="card-header">Task {{ index + 1 }}</h3>
          <div class="card-body">
            
            <div v-if="index > 0" class="mb-4">
              <Checkbox
                v-model="task.is_child"
                @change="handleChildToggle(task)"
                label="Is Child Task"
              />
            </div>

            <!-- Parent Task Select -->
            <div v-if="task.is_child" class="mb-4">
              <Select
                v-model="task.parent_task"
                :options="[
                  { label: 'Select Parent Task', value: null },
                  ...availableParentTasks(index).map((parent, parentIndex) => ({
                    label: parent.task_name || `Task ${parentIndex + 1}`,
                    value: parentIndex
                  }))
                ]"
                label="Parent Task"
                required
              />
            </div>

            <div class="mb-4">
            <Checkbox
              v-model="task.hide_to_client"
              label="Hide this task from client view"
            />
          </div>

            
            <Input
              label="Task Name"
              v-model="task.task_name"
              type="text"
              required
              class="mb-4"
            />

           
            <Select
              v-model="task.task_type"
              :options="[
                { label: 'Select Task Type', value: '' },
                { label: 'Internal', value: 'Internal' },
                { label: 'Client', value: 'Client' }
              ]"
              required
              class="mb-4"
              @change="handleTaskTypeChange(index)"
            />

            <!-- New Fields for Each Task -->
            <div class="grid grid-cols-2 gap-4 mb-4">
              
              <Select
                v-model="task.assign_to"
                :options="getAssignToOptions(task.task_type)"
                label="Assign To"
                required
              />

             
              <Select
                v-model="task.priority"
                :options="priorityOptions"
                label="Priority"
                required
              />
            </div>

            
            <Input
              label="Complete Within Days"
              v-model="task.complete_within_days"
              type="number"
              min="1"
              required
              class="mb-4"
            />

            <!-- Date Range (disabled for child tasks) -->
            <div class="grid grid-cols-2 gap-4 mb-4">
              <Input
                label="From Date"
                v-model="task.from_date"
                type="date"
                :disabled="task.is_child"
                :required="!task.is_child"
              />
              <Input
                label="To Date"
                v-model="task.to_date"
                type="date"
                :disabled="task.is_child"
                :required="!task.is_child"
              />
            </div>

            
            <Textarea
              label="Description"
              v-model="task.description"
              rows="3"
            />
          </div>
        </div>

        
        <Button
          type="button"
          @click="addTask"
          variant="outline"
          class="w-full mb-4"
        >
          + Add Task
        </Button>

        
        <div class="flex gap-3">
          <Button
            type="button"
            @click="cancel"
            variant="outline"
            class="flex-1"
            :disabled="submitting"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="solid"
            theme="gray"
            class="flex-1"
            :loading="submitting"
          >
            {{ submitting ? 'Creating...' : 'Create Activity' }}
          </Button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Input, Textarea, Button, createResource, Select, Checkbox } from 'frappe-ui'

const route = useRoute()
const router = useRouter()

const formData = ref({
  template_name: '',
  is_recurring: false,
  recurring_day: null,
  client: '',
  tasks: []
})


const daysOfMonth = Array.from({length: 31}, (_, i) => ({
  label: (i + 1).toString(),
  value: i + 1
}))

const priorityOptions = [
  { label: 'Low', value: 'Low' },
  { label: 'Medium', value: 'Medium' },
  { label: 'High', value: 'High' }
]

const clientOptions = ref([{ label: 'Select Client', value: '' }])
const clientUsers = ref([])
const internalUsers = ref([])

const loading = ref(true)
const submitting = ref(false)
const showSuccess = ref(false)
const errorMessage = ref('')

// Fetch template data with child tasks
onMounted(async () => {
  try {
    await Promise.all([
      fetchTemplateWithTasks(),
      fetchClients(),
      fetchInternalUsers()
    ])
  } catch (error) {
    errorMessage.value = 'Initialization failed: ' + (error.message || 'Unknown error')
  }
})

const fetchTemplateWithTasks = async () => {
  loading.value = true
  try {
    const resource = createResource({
      url: 'frappe.client.get',
      params: {
        doctype: 'Template',
        name: route.params.templateName,
        fields: ['*']
      }
    })
    
    const templateData = await resource.fetch()
    
    
    const taskNameToIndex = {}
    templateData.tasks.forEach((task, index) => {
      taskNameToIndex[task.name] = index
    })
    
    // Transform the data for our form
    formData.value = {
      template_name: templateData.template_name,
      is_recurring: false,
      recurring_day: null,
      client: '',
      tasks: templateData.tasks.map(task => ({
        ...task,
        is_child: !!task.parent_task,
        // Find the index of the parent task in the tasks array
        parent_task: task.parent_task ? taskNameToIndex[task.parent_task] : null,
        assign_to: '',
        priority: 'Medium'
      }))
    }
    
    if (formData.value.tasks.length === 0) {
      formData.value.tasks.push(createEmptyTask())
    }
  } catch (error) {
    errorMessage.value = error.message || 'Failed to load template data'
  } finally {
    loading.value = false
  }
}

// create an empty task
const createEmptyTask = () => ({
  task_name: '',
  task_type: '',
  complete_within_days: 1,
  from_date: '',
  to_date: '',
  description: '',
  is_child: false,
  parent_task: null,
  assign_to: '',
  priority: 'Medium',
  hide_to_client: false
})


const findParentTaskIndex = (tasks, parentTaskName) => {
  const parentTask = tasks.find(t => t.name === parentTaskName)
  return tasks.indexOf(parentTask)
}

// Fetch clients for select options
const fetchClients = async () => {
  try {
    const resource = createResource({
      url: 'frappe.client.get_list',
      params: {
        doctype: 'ClientFormData',
        fields: ['name', 'client_name']
      }
    });

    const response = await resource.fetch();
    console.log("Full response:", response);

    
    const clients = response.message || response.result || (Array.isArray(response) ? response : []);

    clientOptions.value = [
      { label: 'Select Client', value: '' },
      ...clients.map(client => ({
        label: client.client_name,
        value: client.name
      }))
    ];

    console.log("Options:", clientOptions.value);

  } catch (error) {
    console.error('Failed to load clients:', error);
    errorMessage.value = 'Failed to load client list. Please check your permissions.';
    clientOptions.value = [{ label: 'Failed to load clients', value: '' }];
  }
};

const validateActivityName = async () => {
  if (!formData.value.template_name) return
  
  const nameExists = await checkActivityNameExists(formData.value.template_name)
  if (nameExists) {
    errorMessage.value = 'An activity with this name already exists. Please choose a different name.'
  } else {
    errorMessage.value = ''
  }
}

const checkActivityNameExists = async (activityName) => {
  try {
    const resource = createResource({
      url: 'frappe.client.get_list',
      params: {
        doctype: 'Activity',
        filters: [['activity_name', '=', activityName]],
        limit: 1
      }
    })
    
    const response = await resource.fetch()
    return response.length > 0
  } catch (error) {
    console.error('Error checking activity name:', error)
    return false
  }
}
// Fetch internal users (non-client role)
const fetchInternalUsers = async () => {
  try {
    const resource = createResource({
      url: 'client_management.client_management.doctype.activity.activity.get_users_for_assignment',
      method: 'GET'
    })

    const response = await resource.fetch()
    console.log(response, "Raw response")

    if (response.success) {
      console.log(response.internal_users, "users")
      internalUsers.value = response.internal_users.map(user => ({
        label: user.full_name || user.name,
        value: user.name
      }))
    } else {
      console.log("Error in response")
      throw new Error(response.message || 'Failed to load users')
    }

  } catch (error) {
    console.error('Failed to load internal users:', error)
    errorMessage.value = 'Failed to load user list. Please check your permissions.'
    internalUsers.value = [{ label: 'Failed to load users', value: '' }]
  }
}


const getUserRoles = async (userId) => {
  const { data } = await createResource({
    url: 'frappe.client.get_list',
    params: {
      doctype: 'Has Role',
      fields: ['role'],
      filters: [['parent', '=', userId]]
    }
  }).fetch()
  return data.map(item => item.role)
}

// Handle client change to fetch client users
const handleClientChange = async (clientId) => {
  if (!clientId) {
    clientUsers.value = []
    return
  }

  try {
    const resource = createResource({
      url: 'client_management.client_management.doctype.activity.activity.get_client_users',
      method: 'POST',
      params: { client_id: clientId }
    })
    
    const response = await resource.fetch()
    console.log(response, "clientchange")
    if (response.success) {
      clientUsers.value = response.users.map(user => ({
        label: user.full_name || user.name,
        value: user.name
      }))
    } else {
      throw new Error(data.message || 'Failed to load client users')
    }
  } catch (error) {
    console.error('Failed to load client users:', error)
    errorMessage.value = 'Failed to load client users. Please check your permissions.'
    clientUsers.value = [{ label: 'Failed to load client users', value: '' }]
  }
}

const getAssignToOptions = (taskType) => {
  const options = [{ label: 'Select User', value: '' }]
  
  if (taskType === 'Internal') {
    return [...options, ...internalUsers.value]
  } else if (taskType === 'Client') {
    return [...options, ...clientUsers.value]
  }
  
  return options
}


const handleTaskTypeChange = (index) => {
  // Reset assign_to when task type changes
  formData.value.tasks[index].assign_to = ''
}

// Handle recurring checkbox change
const handleRecurringChange = () => {
  if (!formData.value.is_recurring) {
    formData.value.recurring_day = null
  }
}

// Handle child task toggle
const handleChildToggle = (task) => {
  if (task.is_child) {
    task.from_date = ''
    task.to_date = ''
    task.parent_task = null
  }
}


const availableParentTasks = (currentIndex) => {
  return formData.value.tasks.slice(0, currentIndex)
}


const addTask = () => {
  formData.value.tasks.push(createEmptyTask())
}


const removeTask = (index) => {
  formData.value.tasks.splice(index, 1)
}

const submitForm = async () => {
  submitting.value = true
  showSuccess.value = false
  errorMessage.value = ''
  
  try {
     if (!formData.value.template_name) {
      errorMessage.value = 'Activity Name is required'
      submitting.value = false
      return
    }
    
    const nameExists = await checkActivityNameExists(formData.value.template_name)
    if (nameExists) {
      errorMessage.value = 'An activity with this name already exists. Please choose a different name.'
      submitting.value = false
      return
    }

    
    const tasksToSubmit = formData.value.tasks.map((task, index) => {
      const taskData = {
        task_name: task.task_name,
        task_type: task.task_type,
        complete_within_days: task.complete_within_days,
        description: task.description,
        is_child: task.is_child || false,
        parent_index: task.is_child ? task.parent_task : null,
        assign_to: task.assign_to,
        priority: task.priority,
        client: formData.value.client,
        hide_to_client: task.hide_to_client || false,
      }

      
      if (!task.is_child) {
        taskData.from_date = task.from_date
        taskData.to_date = task.to_date
      }

      return taskData
    })

    // Create the activity
    const resource = createResource({
      url: 'client_management.client_management.doctype.activity.activity.create_activity_from_template',
      method: 'POST',
      params: {
        template_name: formData.value.template_name,
        client: formData.value.client,
        is_recurring: formData.value.is_recurring,
        recurring_day: formData.value.recurring_day,
        tasks: tasksToSubmit
      }
    })

    await resource.submit()
    
    
    showSuccess.value = true
    
    
    setTimeout(() => {
      router.push({ name: 'ActivityList' }) 
    }, 1500)

  } catch (error) {
    errorMessage.value = error.message || 'Failed to create activity'
  } finally {
    submitting.value = false
  }
}


const cancel = () => {
  router.go(-1)
}
</script>

<style scoped>
.card {
  @apply bg-white rounded-lg shadow border border-gray-200;
}
.card-header {
  @apply px-6 py-4 border-b border-gray-200 font-semibold text-lg;
}
.card-body {
  @apply p-6;
}
</style>