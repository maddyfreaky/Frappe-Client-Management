<template>
  <div class="max-w-3xl mx-auto p-6">
    
    <div v-if="loading && !formData.template_name" class="text-center py-8">
      Loading template data...
    </div>

    
    <div v-if="errorMessage" class="mb-4 p-4 bg-red-100 text-red-700 rounded-md">
      {{ errorMessage }}
    </div>

    
    <div v-if="showSuccess" class="mb-4 p-4 bg-green-100 text-green-700 rounded-md">
      Template updated successfully!
    </div>

    
    <div v-if="formData.template_name" class="card">
      <h2 class="card-header">Edit Template</h2>
      <form @submit.prevent="submitForm" class="card-body">
        
        <Input
          label="Template Name"
          v-model="formData.template_name"
          type="text"
          required
          class="mb-4"
        />

        
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

            
            <div v-if="task.is_child" class="mb-4">
              <Select
                v-model="task.parent_task"
                :options="[
                  { label: 'Select Parent Task', value: '' },
                  ...availableParentTasks(index).map((parent, parentIndex) => ({
                    label: parent.task_name || `Task ${parentIndex + 1}`,
                    value: parentIndex
                  }))
                ]"
                label="Parent Task"
                required
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
            />

            
            <Input
              label="Complete Within Days"
              v-model="task.complete_within_days"
              type="number"
              min="1"
              required
              class="mb-4"
            />

            
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
            {{ submitting ? 'Updating...' : 'Update Template' }}
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

const templateName = ref(route.params.name)
const formData = ref({
  template_name: '',
  tasks: []
})

const loading = ref(true)
const submitting = ref(false)
const showSuccess = ref(false)
const errorMessage = ref('')

// Fetch template data with child tasks
onMounted(async () => {
  await fetchTemplateWithTasks()
})

const fetchTemplateWithTasks = async () => {
  loading.value = true
  try {
    const resource = createResource({
      url: 'frappe.client.get',
      params: {
        doctype: 'Template',
        name: templateName.value,
        fields: ['*'],
        // Include child table fields
        fields: ['name', 'template_name', 'tasks.task_name', 'tasks.task_type', 
                'tasks.complete_within_days', 'tasks.from_date', 'tasks.to_date',
                'tasks.description', 'tasks.is_child', 'tasks.parent_task', 'tasks.name']
      }
    })
    
    const templateData = await resource.fetch()
    
    // Transform the data
    formData.value = {
      template_name: templateData.template_name,
      tasks: templateData.tasks.map((task, index, tasksArray) => ({
        name: task.name, // Keep the task name/id for reference
        task_name: task.task_name,
        task_type: task.task_type,
        complete_within_days: task.complete_within_days,
        from_date: task.from_date,
        to_date: task.to_date,
        description: task.description,
        is_child: !!task.parent_task,
        // Find the index of the parent task in the tasks array
        parent_task: task.parent_task 
          ? tasksArray.findIndex(t => t.name === task.parent_task)
          : null
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


const createEmptyTask = () => ({
  name: '', 
  task_name: '',
  task_type: '',
  complete_within_days: 1,
  from_date: '',
  to_date: '',
  description: '',
  is_child: false,
  parent_task: null
})


const findParentTaskIndex = (tasks, parentTaskName) => {
  const parentTask = tasks.find(t => t.task_name === parentTaskName)
  return tasks.indexOf(parentTask)
}

// Add new task
const addTask = () => {
  formData.value.tasks.push(createEmptyTask())
}

// Remove task
const removeTask = (index) => {
  formData.value.tasks.splice(index, 1)
}

// Handle child task toggle
const handleChildToggle = (task) => {
  if (task.is_child) {
    task.from_date = ''
    task.to_date = ''
    task.parent_task = null
  }
}

// Get available parent tasks
const availableParentTasks = (currentIndex) => {
  return formData.value.tasks.slice(0, currentIndex)
}

const submitForm = async () => {
  submitting.value = true
  showSuccess.value = false
  errorMessage.value = ''
  
  try {
    
    const tasksToSubmit = formData.value.tasks.map((task, index) => {
      const taskData = {
        task_name: task.task_name,
        task_type: task.task_type,
        complete_within_days: task.complete_within_days,
        description: task.description,
        is_child: task.is_child || false,
        parent_index: task.is_child ? parseInt(task.parent_task) : null // Ensure number
      }

      // Only include dates if not a child task
      if (!task.is_child) {
        taskData.from_date = task.from_date
        taskData.to_date = task.to_date
      }

      return taskData
    })

    // Update the template with its tasks
    const resource = createResource({
      url: 'client_management.client_management.doctype.template.template.update_template_with_task',
      method: 'POST',
      params: {
        template_name: templateName.value,
        new_template_name: formData.value.template_name,
        tasks: tasksToSubmit
      }
    })

    await resource.submit()
     
    showSuccess.value = true
    
    
    setTimeout(() => {
      router.push({ name: 'TemplateList' })
    }, 1500)

  } catch (error) {
    errorMessage.value = error.message || 'Failed to update template'
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