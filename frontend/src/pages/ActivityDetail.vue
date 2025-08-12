<template>
  <div class="max-w-4xl mx-auto p-6">
  
    <Button
      icon-left="arrow-left"
      variant="ghost"
      class="mb-4"
      @click="router.go(-1)"
    >
      Back to Activities
    </Button>

    
    <div v-if="loading" class="text-center py-8">
      Loading activity details...
    </div>

    
    <div v-if="errorMessage" class="mb-4 p-4 bg-red-100 text-red-700 rounded-md">
      {{ errorMessage }}
    </div>

    <!-- Activity Details -->
    <div v-if="!loading && activity" class="space-y-6">
      
      <div class="bg-white rounded-lg shadow p-6">
        <div class="flex justify-between items-start">
          <div>
            <h1 class="text-2xl font-semibold">{{ activity.activity_name }}</h1>
            <div class="flex items-center mt-2 space-x-4 text-sm text-gray-600">
              <span>Created by: {{ activity.owner }}</span>
              <span>Created at: {{ formatDate(activity.creation) }}</span>
            </div>
          </div>
          <Badge :theme="activity.is_recurring ? 'green' : 'gray'">
            {{ activity.is_recurring ? 'Recurring' : 'One-time' }}
          </Badge>
        </div>

        <div class="mt-4 grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-500">Client</label>
            <p class="mt-1 text-sm text-gray-900">{{ activity.client }}</p>
          </div>
          <div v-if="activity.is_recurring">
            <label class="block text-sm font-medium text-gray-500">Recurring Day</label>
            <p class="mt-1 text-sm text-gray-900">{{ activity.recurring_day }}</p>
          </div>
        </div>
      </div>

      
      <div class="bg-white rounded-lg shadow overflow-hidden">
        <div class="px-6 py-4 border-b border-gray-200">
          <h2 class="text-lg font-medium">Tasks</h2>
        </div>

        
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Task Name
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Assigned To
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  From Date
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  To Date
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Due Days
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="task in filteredTasks" :key="task.name">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900">{{ task.task_name }}</div>
                  <div v-if="task.description" class="text-sm text-gray-500 mt-1">
                    {{ task.description }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <Badge :theme="task.task_type === 'Internal' ? 'blue' : 'green'">
                    {{ task.task_type }}
                  </Badge>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ task.assigned_to_name || task.assigned_to }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <Badge :theme="getStatusBadgeTheme(task.status)">
                    {{ task.status || 'Not Started' }}
                  </Badge>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ task.from_date ? formatDate(task.from_date) : '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ task.to_date ? formatDate(task.to_date) : '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ task.complete_within_days || '-' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        
        <div v-if="filteredTasks.length === 0" class="p-8 text-center text-gray-500">
          No tasks found
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, Badge, createResource } from 'frappe-ui'

const route = useRoute()
const router = useRouter()


const activity = ref(null)
const tasks = ref([])
const loading = ref(true)
const errorMessage = ref('')
const userRoleProfile = ref('')


const filteredTasks = computed(() => {
  const isClient = userRoleProfile.value === 'Client'
  return isClient 
    ? tasks.value.filter(task => !task.hide_to_client)
    : tasks.value
})


const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}


const getStatusBadgeTheme = (status) => {
  switch (status) {
    case 'Completed': return 'green'
    case 'In Progress': return 'blue'
    case 'Overdue': return 'red'
    default: return 'gray'
  }
}


const getCurrentUser = async () => {
  const resource = createResource({
    url: 'frappe.client.get',
    params: {
      doctype: 'User',
      name: 'Administrator', 
      fields: ['role_profile_name']
    }
  })
  return await resource.fetch()
}

const fetchActivityDetails = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    // First get current user
    const userResource = createResource({
      url: 'frappe.auth.get_logged_user'
    })
    const username = await userResource.fetch()
    
    // Then get user role profile
    const profileResource = createResource({
      url: 'frappe.client.get_value',
      params: {
        doctype: 'User',
        fieldname: 'role_profile_name',
        filters: { name: username }
      }
    })
    const profileData = await profileResource.fetch()
    userRoleProfile.value = profileData.message?.role_profile_name || ''

    
    const activityResource = createResource({
      url: 'frappe.client.get',
      params: {
        doctype: 'Activity',
        name: route.params.activityName,
        fields: ['*']
      }
    })
    activity.value = await activityResource.fetch()

    
    const tasksResource = createResource({
      url: 'client_management.client_management.doctype.activity.activity.get_activity_tasks',
      method: 'GET',
      params: {
        activity_name: route.params.activityName
      }
    })
    const tasksResponse = await tasksResource.fetch()
    
    if (tasksResponse.success) {
      tasks.value = tasksResponse.tasks
    } else {
      throw new Error(tasksResponse.message || 'Failed to load tasks')
    }
  } catch (error) {
    errorMessage.value = error.message || 'Failed to load activity details'
  } finally {
    loading.value = false
  }
}


onMounted(() => {
  fetchActivityDetails()
})
</script>

<style scoped>

</style>