<template>
  <div class="max-w-3xl mx-auto p-6">
    <!-- Success/Error Messages -->
    <div v-if="showSuccess" class="mb-4 p-4 bg-green-100 text-green-700 rounded-md">
      Template created successfully!
    </div>
    <div v-if="showError" class="mb-4 p-4 bg-red-100 text-red-700 rounded-md">
      {{ errorMessage }}
    </div>

    <div class="card">
      <h2 class="card-header">Create New Template</h2>
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
                    @change="handleChildToggle(task, index)"
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

        
        <Button
          type="submit"
          :variant="'solid'"
    :ref_for="true"
    theme="gray"
    size="sm"
    label="Button"

          :loading="loading"
          class="w-full"
        >
          {{ loading ? 'Saving...' : 'Create Template' }}
        </Button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Input, Textarea, Button, createResource, Select, Checkbox } from 'frappe-ui'

const formData = ref({
  template_name: '',
  tasks: [{
    task_name: '',
    task_type: '',
    complete_within_days: 1,
    from_date: '',
    to_date: '',
    description: '',
    is_child: false,
    parent_task: null
  }]
})

const loading = ref(false)
const showSuccess = ref(false)
const showError = ref(false)
const errorMessage = ref('')


const addTask = () => {
  formData.value.tasks.push({
    task_name: '',
    task_type: '',
    complete_within_days: 1,
    from_date: '',
    to_date: '',
    description: '',
    is_child: false,
    parent_task: null
  })
}


const removeTask = (index) => {
  formData.value.tasks.splice(index, 1)
}


const handleChildToggle = (task, index) => {
  if (task.is_child) {
    task.from_date = ''
    task.to_date = ''
  }
}

const availableParentTasks = (currentIndex) => {
  return formData.value.tasks.slice(0, currentIndex)
}

const submitForm = async () => {
  
  showSuccess.value = false
  showError.value = false
  errorMessage.value = ''
  
  loading.value = true
  
  try {
    
    const tasksToSubmit = formData.value.tasks.map((task, index) => {
      const taskData = {
        task_name: task.task_name,
        task_type: task.task_type,
        complete_within_days: task.complete_within_days,
        description: task.description,
        is_child: task.is_child || false,
        parent_index: task.is_child ? parseInt(task.parent_task) : null 
      }

      if (!task.is_child) {
        taskData.from_date = task.from_date
        taskData.to_date = task.to_date
      }

      return taskData
    })

    const resource = createResource({
      url: 'client_management.client_management.doctype.template.template.create_template_with_task',
      method: 'POST',
      params: {
        template_name: formData.value.template_name,
        tasks: tasksToSubmit
      }
    })

    await resource.submit()
    
   
    showSuccess.value = true
    
    
    formData.value = {
      template_name: '',
      tasks: [{
        task_name: '',
        task_type: '',
        complete_within_days: 1,
        from_date: '',
        to_date: '',
        description: '',
        is_child: false,
        parent_task: null
      }]
    }

    
    setTimeout(() => {
      showSuccess.value = false
    }, 3000)

  } catch (error) {
    
    showError.value = true
    errorMessage.value = error.message || 'Failed to create template'
  } finally {
    loading.value = false
  }
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