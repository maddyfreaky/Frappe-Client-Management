<template>
  <div class="max-w-7xl mx-auto p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-semibold">My Tasks</h1>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-8">
      Loading tasks...
    </div>

    

    <!-- Tasks Table -->
    <div v-if="!loading" class="bg-white rounded-lg shadow overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th v-for="column in columns" :key="column.key" scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {{ column.label }}
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            Comments
        </th> 
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="task in tasks" :key="task.name" :class="{'opacity-50': isTaskDisabled(task)}">
              <td class="px-6 py-4 whitespace-nowrap">
                <a href="#" @click.prevent="openTaskModal(task)" class="text-indigo-600 hover:text-indigo-900">
                  {{ task.task_name }}
                </a>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                {{ task.activity_name }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                {{ formatDate(task.from_date) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                {{ formatDate(task.to_date) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="priorityClass(task.priority)" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                  {{ task.priority }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="relative">
                  <select 
                    v-model="task.status" 
                    @focus="previousStatus = task.status"
                    @change="updateStatus(task)"
                    :disabled="isTaskDisabled(task) || task.updating"
                    class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                  >
                    <option v-for="option in statusOptions" :key="option" :value="option">
                      {{ option }}
                    </option>
                  </select>
                  <svg 
                    v-if="task.updating"
                    class="animate-spin h-5 w-5 text-indigo-600 absolute right-2 top-2" 
                    xmlns="http://www.w3.org/2000/svg" 
                    fill="none" 
                    viewBox="0 0 24 24"
                  >
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex space-x-2">
                  <button 
                    v-if="!isClient"
                    @click="openCommentModal(task, 'Internal')"
                    class="p-1 rounded-md bg-blue-100 text-blue-800 hover:bg-blue-200"
                    title="Internal Comments"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0010 11z" clip-rule="evenodd" />
                    </svg>
                  </button>
                  <button 
                    @click="openCommentModal(task, 'External')"
                    class="p-1 rounded-md bg-green-100 text-green-800 hover:bg-green-200"
                    title="External Comments"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Comment Modal -->
  <div v-if="showCommentModal" class="fixed inset-0 z-50 overflow-y-auto">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 transition-opacity" aria-hidden="true">
        <div class="absolute inset-0 bg-gray-500 opacity-75" @click="closeCommentModal"></div>
      </div>

      <!-- Modal container -->
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div class="sm:flex sm:items-start">
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
              <h3 class="text-lg leading-6 font-medium text-gray-900">
                {{ selectedCommentType }} Comments - Activity: {{ currentActivity.activity_name }}
              </h3>
              <div class="mt-4">
                <!-- Comments List -->
                <div class="border rounded-lg p-4 max-h-96 overflow-y-auto mb-4">
                  <div v-for="comment in comments" :key="comment.name" class="mb-4 last:mb-0">
                    <div class="flex justify-between items-start">
                      <div class="font-medium">{{ comment.user_fullname || comment.comment_by.split('@')[0] }}</div>
                      <div class="text-sm text-gray-500">{{ formatDateTime(comment.comment_date) }}</div>
                    </div>
                    <div class="mt-1 text-sm text-gray-800">{{ comment.comment }}</div>
                    <div v-if="comment.attachment" class="mt-2">
                      <a :href="comment.attachment" target="_blank" class="text-blue-600 hover:text-blue-800 text-sm">
                        View Attachment
                      </a>
                    </div>
                  </div>
                </div>

                <!-- New Comment Form -->
                <div class="border-t pt-4">
                  <textarea
                    v-model="newComment"
                    class="w-full border rounded-md p-2"
                    rows="3"
                    placeholder="Type your comment here..."
                  ></textarea>
                  <div class="flex justify-between items-center mt-2">
                    <div class="flex items-center space-x-2">
                      <input
                        type="file"
                        ref="fileInput"
                        @change="handleFileUpload"
                        class="hidden"
                      />
                      <button
                        @click="$refs.fileInput.click()"
                        class="text-sm text-gray-600 hover:text-gray-800"
                      >
                        Attach File
                      </button>
                      <span v-if="attachment" class="text-sm text-gray-600 flex items-center">
                        {{ attachment.name }}
                        <button @click="removeAttachment" class="ml-1 text-red-500 hover:text-red-700">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                          </svg>
                        </button>
                      </span>
                    </div>
                    <button
                      @click="submitComment"
                      class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                      :disabled="!newComment"
                    >
                      Post Comment
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button
            type="button"
            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            @click="closeCommentModal"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>

    <!-- Task Details Modal -->
    <Dialog
      v-model="showTaskModal"
      :title="selectedTask.task_name || 'Task Details'"
      size="xl"
      :dismissable="true"
    >
      <div v-if="selectedTask.name" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Activity</label>
            <p class="mt-1 text-sm text-gray-900">{{ selectedTask.activity_name }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Status</label>
            <p class="mt-1 text-sm text-gray-900">{{ selectedTask.status }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">From Date</label>
            <p class="mt-1 text-sm text-gray-900">{{ formatDate(selectedTask.from_date) }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">To Date</label>
            <p class="mt-1 text-sm text-gray-900">{{ formatDate(selectedTask.to_date) }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Priority</label>
            <p class="mt-1 text-sm text-gray-900">{{ selectedTask.priority }}</p>
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Description</label>
          <p class="mt-1 text-sm text-gray-900 whitespace-pre-line">{{ selectedTask.description }}</p>
        </div>
      </div>
      <div v-else class="text-center py-8">
        Loading task details...
      </div>
      <template #actions>
        <Button
          variant="solid"
          @click="showTaskModal = false"
        >
          Close
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Button, Dialog, createResource } from 'frappe-ui'

const columns = [
  { label: 'Task Name', key: 'task_name' },
  { label: 'Activity', key: 'activity_name' },
  { label: 'From Date', key: 'from_date' },
  { label: 'To Date', key: 'to_date' },
  { label: 'Priority', key: 'priority' },
  { label: 'Status', key: 'status' }
]

const statusOptions = ['Not Started', 'Working', 'Completed']

const tasks = ref([])
const loading = ref(true)
const errorMessage = ref('')
const showTaskModal = ref(false)
const selectedTask = ref({
  task_name: '',
  activity_name: '',
  status: '',
  from_date: '',
  to_date: '',
  priority: '',
  description: ''
})
const previousStatus = ref(null)

const showCommentModal = ref(false)
const selectedCommentType = ref('')
const comments = ref([])
const newComment = ref('')
const attachment = ref(null)
const fileInput = ref(null)
const currentActivity = ref({})

const openCommentModal = async (task, commentType) => {
  resetCommentForm()
  selectedCommentType.value = commentType
  currentActivity.value = {
    name: task.activity_docname,
    activity_name: task.activity_name
  }
  showCommentModal.value = true
  await fetchComments()
}

const closeCommentModal = () => {
  resetCommentForm()
  showCommentModal.value = false
}

const resetCommentForm = () => {
  newComment.value = ''
  attachment.value = null
  if (fileInput.value) fileInput.value.value = ''
}

const removeAttachment = () => {
  attachment.value = null
  if (fileInput.value) fileInput.value.value = ''
}

const isClient = ref(false);

// Fetch client status when component mounts
onMounted(async () => {
  try {
    const response = await fetch('/api/method/client_management.client_management.doctype.activity_comment.activity_comment.is_user_client');
    const result = await response.json();
    isClient.value = result.message || false;
  } catch (error) {
    console.error("Error checking user role:", error);
    isClient.value = false;
  }
});

const formatDateTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString() 
}



const fetchComments = async () => {
  try {
    const resource = createResource({
      url: 'client_management.client_management.doctype.activity_comment.activity_comment.get_activity_comments',
      method: 'GET',
      params: {
        activity_name: currentActivity.value.name,
        comment_type: selectedCommentType.value
      }
    });

    const response = await resource.fetch();

    if (response.success) {
      comments.value = response.comments.map(comment => ({
        ...comment,
        user_fullname: comment.comment_by_fullname || comment.comment_by.split('@')[0],
      }));
    }
  } catch (error) {
    console.error("Error fetching comments:", error);
  }
};



const handleFileUpload = (e) => {
  const file = e.target.files[0]
  if (file) {
    attachment.value = file
  }
}

const submitComment = async () => {
  try {
    if (!newComment.value.trim()) {
      errorMessage.value = "Please enter a comment";
      return;
    }

    const formData = new FormData();
    formData.append('activity_name', currentActivity.value.name);
    formData.append('comment_type', selectedCommentType.value);
    formData.append('comment', newComment.value.trim());

    if (attachment.value) {
      formData.append('file', attachment.value);
    }

    // Add CSRF token if available
    if (window.frappe?.csrf_token) {
      formData.append('csrf_token', window.frappe.csrf_token);
    }

    // Create temporary comment
    const tempId = 'temp-' + Date.now();
    const currentUser = window.frappe?.session?.user || 'Unknown User';
    console.log(currentUser,"Current user")
    const userFullname =
      window.frappe?.boot?.user_info?.[currentUser]?.fullname || currentUser.split('@')[0];

    const tempComment = {
      name: tempId,
      comment: newComment.value.trim(),
      comment_by: currentUser,
      comment_by_fullname: userFullname,
      user_fullname: userFullname,
      comment_date: new Date().toISOString(),
      is_temp: true,
      attachment: null,
    };

    
    comments.value.unshift(tempComment);
    resetCommentForm();

    const response = await fetch(
      '/api/method/client_management.client_management.doctype.activity_comment.activity_comment.add_activity_comment',
      {
        method: 'POST',
        body: formData,
      }
    );

    const result = await response.json();

    if (result.success) {
      const index = comments.value.findIndex(c => c.name === tempId);
      if (index !== -1) {
        comments.value[index] = {
          name: result.comment_id,
          comment: newComment.value.trim(),
          comment_by: currentUser,
          comment_by_fullname: result.user_fullname,
          user_fullname: result.user_fullname,
          comment_date: result.comment_date,
          is_temp: false,
          attachment: result.attachment_url || null,
        };
      }
    } else {
      comments.value = comments.value.filter(c => c.name !== tempId);
      errorMessage.value = result.message || "Failed to submit comment";
    }
  } catch (error) {
    console.error("Comment submission failed:", error);
    errorMessage.value = "Failed to submit comment. Please try again.";
  }
};



const createFileFormData = () => {
  const formData = new FormData()
  formData.append('file', attachment.value)
  formData.append('doctype', 'Activity Comment')
  formData.append('fieldname', 'attachment')
  formData.append('is_private', 1)
  return formData
}

// Format date
const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

// Priority badge class
const priorityClass = (priority) => {
  const classes = {
    'High': 'bg-red-100 text-red-800',
    'Medium': 'bg-yellow-100 text-yellow-800',
    'Low': 'bg-green-100 text-green-800'
  }
  return classes[priority] || 'bg-gray-100 text-gray-800'
}

// Check if task should be disabled
const isTaskDisabled = (task) => {
  return task.parent_task && task.parent_status !== 'Completed'
}

// Open task modal
const openTaskModal = (task) => {
  selectedTask.value = { ...task }
  showTaskModal.value = true
}

// Update task status
const updateStatus = async (task) => {
  task.updating = true
  
  try {
    const resource = createResource({
      url: 'client_management.client_management.doctype.activity.activity.update_activity_task_status',
      method: 'POST',
      params: {
        activity_name: task.activity_docname,
        task_name: task.name,
        status: task.status
      }
    })
    
    await resource.submit()
    await fetchTasks() // Refresh the task list
  } catch (error) {
    console.error("Status update failed:", error)
    // Revert the status in UI
    task.status = previousStatus.value
  } finally {
    task.updating = false
  }
}

// Fetch tasks
const fetchTasks = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    const resource = createResource({
      url: 'client_management.client_management.doctype.activity.activity.get_user_activity_tasks',
      method: 'GET'
    })
    
    const response = await resource.fetch()
    
    if (response.success) {
      tasks.value = response.tasks.map(task => ({
        ...task,
        parent_status: task.parent_status || null,
        updating: false // Initialize updating flag
      }))
    } else {
      throw new Error(response.message || 'Failed to load tasks')
    }
  } catch (error) {
    errorMessage.value = error.message || 'Failed to load tasks'
  } finally {
    loading.value = false
  }
}

// Initialize
onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>

.opacity-50 {
  opacity: 0.5;
  pointer-events: none;
}

.animate-spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>