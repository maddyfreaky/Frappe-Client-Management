<template>
  <div class="max-w-7xl mx-auto p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-semibold">My Activities</h1>
      <Button
        icon-left="plus"
        @click="router.push({ name: 'Template Tasks' })"
      >
        New Activity
      </Button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      Loading activities...
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="mb-4 p-4 bg-red-100 text-red-700 rounded-md">
      {{ errorMessage }}
    </div>

    <!-- Activities Table -->
    <div v-if="!loading && activities.length > 0" class="bg-white rounded-lg shadow overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th v-for="column in columns" :key="column.key" scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {{ column.label }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="activity in activities" :key="activity.name">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ activity.activity_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="activity.is_recurring ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                  {{ activity.is_recurring ? 'Yes' : 'No' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ activity.owner }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(activity.creation) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ activity.task_count || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ activity.client_name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
               <button @click="viewActivity(activity.name)" class="text-indigo-600 hover:text-indigo-900 mr-3">
                View
                </button>
               <button @click="confirmDelete(activity)" class="text-red-600 hover:text-red-900">
    Delete
  </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    
    <div v-if="!loading && activities.length === 0" class="bg-white rounded-lg shadow p-8 text-center">
      <p class="text-gray-500">No activities found</p>
    </div>

    <!-- Custom Pagination -->
    <div v-if="activities.length > 0" class="mt-4 flex justify-between items-center">
      <div class="text-sm text-gray-600">
        Showing {{ activities.length }} of {{ totalCount }} activities
      </div>
      <div class="flex gap-2">
        <Button
          @click="prevPage"
          :disabled="currentPage === 1"
          variant="outline"
          size="sm"
        >
          Previous
        </Button>
        <span class="px-4 py-2 text-sm">
          Page {{ currentPage }} of {{ totalPages }}
        </span>
        <Button
          @click="nextPage"
          :disabled="currentPage >= totalPages"
          variant="outline"
          size="sm"
        >
          Next
        </Button>
      </div>
    </div>

    
   <div v-if="showDeleteDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl w-full max-w-md">
      <!-- Dialog Header -->
      <div class="border-b px-6 py-4">
        <h3 class="text-lg font-medium text-gray-900">Confirm Delete</h3>
      </div>
      
      <!-- Dialog Body -->
      <div class="p-6">
        <p class="text-gray-700 mb-6">Are you sure you want to delete this activity?</p>
        
        <!-- Dialog Actions -->
        <div class="flex justify-end space-x-3">
          <button
            @click="showDeleteDialog = false"
            class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="deleteActivity"
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
            :disabled="deleting"
          >
            <span v-if="deleting">Deleting...</span>
            <span v-else>Delete</span>
          </button>
        </div>
      </div>
    </div>
  </div>


  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Dialog, createResource } from 'frappe-ui'

const router = useRouter()

const viewActivity = (activityName) => {
  router.push({
    name: 'ActivityDetail',
    params: { activityName }
  })
}


const columns = [
  { label: 'Activity Name', key: 'activity_name' },
  { label: 'Recurring', key: 'recurring' },
  { label: 'Created By', key: 'owner' },
  { label: 'Created At', key: 'creation' },
  { label: 'Tasks', key: 'task_count' },
  { label: 'Client', key: 'client' },
  { label: 'Actions', key: 'actions' }
]


const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}


const activities = ref([])
const loading = ref(true)
const errorMessage = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)
const showDeleteDialog = ref(false)
const deleting = ref(false)
const activityToDelete = ref(null)


const fetchActivities = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const resource = createResource({
      url: 'client_management.client_management.doctype.activity.activity.get_user_activities',
      method: 'GET',
      params: {
        page: currentPage.value
      }
    })
    
    const response = await resource.fetch()
    
    if (response.success) {
      activities.value = response.activities.map(activity => ({
        ...activity,
        task_count: activity.tasks_count || 0
      }))
      totalCount.value = response.total_count
      totalPages.value = response.total_pages
    } else {
      throw new Error(response.message || 'Failed to load activities')
    }
  } catch (error) {
    errorMessage.value = error.message || 'Failed to load activities'
  } finally {
    loading.value = false
  }
}

// Pagination methods
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchActivities()
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchActivities()
  }
}


const editActivity = (activityName) => {
  router.push({
    name: 'ActivityForm',
    params: { activityName }
  })
}

const confirmDelete = (activity) => {
  activityToDelete.value = activity;
  showDeleteDialog.value = true;
};

const deleteActivity = async () => {
  deleting.value = true;
  try {
    const resource = createResource({
      url: 'frappe.client.delete',
      method: 'POST',
      params: {
        doctype: 'Activity',
        name: activityToDelete.value.name
      }
    });
    
    await resource.submit();
    showDeleteDialog.value = false;
    fetchActivities();
  } catch (error) {
    errorMessage.value = error.message || 'Failed to delete activity';
  } finally {
    deleting.value = false;
  }
};


onMounted(() => {
  fetchActivities()
})
</script>

<style scoped>

</style>