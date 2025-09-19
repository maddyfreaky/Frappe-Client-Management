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
         <!-- Search Field -->
    <div class="mt-4">
      <div class="relative rounded-md shadow-sm max-w-md">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
          </svg>
        </div>
        <input
          v-model="searchQuery"
          type="text"
          class="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-10 sm:text-sm border-gray-300 rounded-md py-2"
          placeholder="Search ..."
          @input="filterTasks"
        />
      </div>
    </div>

        <table class="min-w-full divide-y divide-gray-200 mt-5">
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
            <tr v-for="task in paginatedTasks" :key="task.name" :class="{'opacity-50': isTaskDisabled(task)}">
             
              <td class="px-6 py-4 whitespace-nowrap">
                {{ task.activity_name }}
              </td>

              <td class="px-6 py-4 whitespace-nowrap">
              <router-link :to="`/tasks/${task.name}`" class="text-indigo-600 hover:text-indigo-900">
                {{ task.task_name }}
              </router-link>
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
      @change="handleStatusChange(task)"
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
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="CurrentColor">
                      <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <!-- Pagination Controls -->
        <div class="flex items-center justify-between px-6 py-3 bg-white border-t border-gray-200">
          <div class="flex-1 flex justify-between sm:hidden">
            <button 
              @click="currentPage = currentPage - 1" 
              :disabled="currentPage === 1"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Previous
            </button>
            <button 
              @click="currentPage = currentPage + 1" 
              :disabled="currentPage === totalPages"
              class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Next
            </button>
          </div>
          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                Showing
                <span class="font-medium">{{ (currentPage - 1) * pageSize + 1 }}</span>
                to
                <span class="font-medium">{{ Math.min(currentPage * pageSize, filteredTasks.length) }}</span>
                of
                <span class="font-medium">{{ filteredTasks.length }}</span>
                results
              </p>
            </div>
            <div>
              <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <button 
                  @click="currentPage = currentPage - 1" 
                  :disabled="currentPage === 1"
                  :class="{'opacity-50 cursor-not-allowed': currentPage === 1, 'hover:bg-gray-50': currentPage > 1}"
                  class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500"
                >
                  <span class="sr-only">Previous</span>
                  <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </button>
                
                <!-- Page numbers -->
                <button 
                  v-for="page in visiblePages" 
                  :key="page"
                  @click="currentPage = page"
                  :class="{'z-10 bg-indigo-50 border-indigo-500 text-indigo-600': currentPage === page, 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50': currentPage !== page}"
                  class="relative inline-flex items-center px-4 py-2 border text-sm font-medium"
                >
                  {{ page }}
                </button>
                
                <button 
                  @click="currentPage = currentPage + 1" 
                  :disabled="currentPage === totalPages"
                  :class="{'opacity-50 cursor-not-allowed': currentPage === totalPages, 'hover:bg-gray-50': currentPage < totalPages}"
                  class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500"
                >
                  <span class="sr-only">Next</span>
                  <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                  </svg>
                </button>
              </nav>
            </div>
            
            <!-- Page size selector -->
            <div class="flex items-center">
              <span class="text-sm text-gray-700 mr-2 text-nowrap">Rows per page:</span>
              <select 
                v-model="pageSize" 
                @change="currentPage = 1"
                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              >
                <option v-for="option in pageSizeOptions" :key="option" :value="option">
                  {{ option }}
                </option>
              </select>
            </div>
          </div>
          
        </div>
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
                  <div v-if="comment.is_temp" class="mt-1 text-xs text-gray-500">
                    Posting...
                  </div>
                  
                  <!-- Seen By Section - Only show for the last comment -->
                  <div v-if="isLastComment(comment) && seenByUsers.length > 0" class="mt-2 pt-2 border-t border-gray-100">
                  <div class="flex items-center text-xs text-gray-500">
                    <span class="mr-1">Seen by:</span>
                    <div class="flex flex-wrap">
                      <span v-for="user in seenByUsers" :key="user.user" class="mr-2">
                        {{ user.full_name || user.user }}
                      </span>
                    </div>
                  </div>
                </div>
                </div>
              </div>

              <!-- Seen By Footer -->
              <div v-if="comments.length > 0 && seenByUsers.length > 0" class="flex items-center text-xs text-gray-500 mb-2">
  <span class="mr-1">Seen by:</span>
  <div class="flex flex-wrap">
    <span v-for="user in seenByUsers" :key="user.user" class="mr-2">
      {{ user.full_name || user.user }}
    </span>
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
import { ref, computed, onMounted, watch } from 'vue'
import { Button, Dialog, createResource } from 'frappe-ui'

const columns = [
  { label: 'Activity', key: 'activity_name' },
  { label: 'Task Name', key: 'task_name' },
  { label: 'From Date', key: 'from_date' },
  { label: 'To Date', key: 'to_date' },
  { label: 'Priority', key: 'priority' },
  { label: 'Status', key: 'status' }
]

const statusOptions = ['Not Started', 'Working', 'Completed']

const seenByUsers = ref([]);
const seenByInterval = ref(null);
const hasMarkedAsSeen = ref(false);
const currentActivityKey = ref('');
const latestCommentTime = ref(null);
const latestCommentId = ref(null);



const tasks = ref([])
const filteredTasks = ref([])
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

// Search query - Moved to the top to avoid reference errors
const searchQuery = ref('')

// Pagination variables
const currentPage = ref(1)
const pageSize = ref(10)
const pageSizeOptions = [5, 10, 20, 50]

// Pagination computed properties
const totalPages = computed(() => {
  return Math.ceil(filteredTasks.value.length / pageSize.value)
})

const paginatedTasks = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value
  return filteredTasks.value.slice(startIndex, startIndex + pageSize.value)
})

const visiblePages = computed(() => {
  const maxVisiblePages = 5
  const halfVisible = Math.floor(maxVisiblePages / 2)
  
  let startPage = Math.max(1, currentPage.value - halfVisible)
  let endPage = Math.min(totalPages.value, startPage + maxVisiblePages - 1)
  
  if (endPage - startPage + 1 < maxVisiblePages) {
    startPage = Math.max(1, endPage - maxVisiblePages + 1)
  }
  
  const pages = []
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i)
  }
  
  return pages
})

// Watch for changes to reset to first page
watch(searchQuery, () => {
  currentPage.value = 1
})

watch(filteredTasks, () => {
  currentPage.value = 1
})

const isLastComment = (comment) => {
  return comments.value.length > 0 && comment.name === comments.value[0].name;
};

// API call to mark comments as seen
const markCommentAsSeen = async (commentId) => {
  if (!showCommentModal.value || !commentId) {
    return { success: true };
  }
  
  try {
    const formData = new FormData();
    formData.append('comment_id', commentId);
    
    // Add CSRF token if available
    if (window.frappe?.csrf_token) {
      formData.append('csrf_token', window.frappe.csrf_token);
    }

    const response = await fetch(
      '/api/method/client_management.client_management.doctype.activity_comment.activity_comment.mark_comment_as_seen',
      {
        method: 'POST',
        body: formData,
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    return result;
  } catch (error) {
    console.error('Error marking comment as seen:', error);
    return { success: false, error: error.message };
  }
};

// API call to get seen by users
const fetchSeenByUsers = async (commentId) => {
  if (!showCommentModal.value || !commentId) return;
  
  try {
    const resource = createResource({
      url: 'client_management.client_management.doctype.activity_comment.activity_comment.get_comment_seen_by',
      method: 'GET',
      params: {
        comment_id: commentId
      }
    });

    const response = await resource.fetch();
    
    let users = [];
    if (response.success) {
      users = response.users || [];
    } else if (response.message && response.message.success) {
      users = response.message.users || [];
    }
    
    // Filter out duplicates on client side
    const uniqueUsers = [];
    const seenUsers = new Set();
    
    for (const user of users) {
      if (!seenUsers.has(user.user)) {
        seenUsers.add(user.user);
        uniqueUsers.push(user);
      }
    }
    
    seenByUsers.value = uniqueUsers;
    
  } catch (error) {
    console.error('Error fetching seen by users:', error);
    seenByUsers.value = [];
  }
};


const trackSeenBy = async () => {
  if (!latestCommentId.value) return;
  
  try {
    // Mark the latest comment as seen
    const markResult = await markCommentAsSeen(latestCommentId.value);
    
    // Fetch users who have seen the latest comment
    await fetchSeenByUsers(latestCommentId.value);
    
  } catch (error) {
    console.error('Error in trackSeenBy:', error);
  }
};


const setupSeenByTracking = () => {
  // Clear any existing interval
  if (seenByInterval.value) {
    clearInterval(seenByInterval.value);
    seenByInterval.value = null;
  }
  
  // Start tracking if modal is open
  if (showCommentModal.value) {
    // Track immediately
    trackSeenBy();
    
    // Set up interval to update seen by list periodically
    seenByInterval.value = setInterval(trackSeenBy, 30000); // Update every 30 seconds
  }
};



const openCommentModal = async (task, commentType) => {
  resetCommentForm();
  selectedCommentType.value = commentType;
  currentActivity.value = {
    name: task.activity_docname,
    activity_name: task.activity_name
  };
  console.log(seenByUsers)
  showCommentModal.value = true;
  // Use explicit parameters when fetching comments
  await fetchComments(task.activity_docname, commentType);
  setupSeenByTracking();
};

const closeCommentModal = () => {
  resetCommentForm();
  showCommentModal.value = false;
if (seenByInterval.value) {
    clearInterval(seenByInterval.value);
    seenByInterval.value = null;
  }
  seenByUsers.value = [];
  console.log(seenByUsers)
  hasMarkedAsSeen.value = false;
  currentActivityKey.value = '';
  latestCommentTime.value = null;
};

watch(showCommentModal, (newValue) => {
  if (newValue) {
    // Small delay to ensure DOM is rendered
    setTimeout(setupSeenByTracking, 100);
  } else {
    if (seenByInterval.value) {
      clearInterval(seenByInterval.value);
      seenByInterval.value = null;
    }
    seenByUsers.value = [];
  }
});

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

const fetchComments = async (activityName = null, commentType = null) => {
  try {
    const activityNameToUse = activityName || currentActivity.value.name;
    const commentTypeToUse = commentType || selectedCommentType.value;
    
    if (!activityNameToUse || !commentTypeToUse) {
      console.error("Missing parameters for fetching comments");
      return;
    }

    const resource = createResource({
      url: 'client_management.client_management.doctype.activity_comment.activity_comment.get_activity_comments',
      method: 'GET',
      params: {
        activity_name: activityNameToUse,
        comment_type: commentTypeToUse
      }
    });

    const response = await resource.fetch();

    if (response.success) {
      comments.value = response.comments.map(comment => ({
        ...comment,
        user_fullname: comment.comment_by_fullname || comment.comment_by.split('@')[0],
      }));
      
      if (comments.value.length > 0) {
        // Store the latest comment ID for "seen by" tracking
        latestCommentId.value = comments.value[0].name;
        console.log('Latest comment ID:', latestCommentId.value);
        
        // Fetch seen by users for the latest comment
        await fetchSeenByUsers(latestCommentId.value);
      }
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

    const commentText = newComment.value.trim();

    const formData = new FormData();
    formData.append('activity_name', currentActivity.value.name);
    formData.append('comment_type', selectedCommentType.value);
    formData.append('comment', commentText);

    if (attachment.value) {
      formData.append('file', attachment.value);
    }

    if (window.frappe?.csrf_token) {
      formData.append('csrf_token', window.frappe.csrf_token);
    }

    // Show loading state
    const loadingComment = {
      name: 'loading-' + Date.now(),
      comment: commentText,
      comment_by: window.frappe?.session?.user || 'Unknown User',
      comment_by_fullname: 'Posting...',
      user_fullname: 'Posting...',
      comment_date: new Date().toISOString(),
      is_loading: true,
      attachment: null,
    };
    
    comments.value.unshift(loadingComment);
    resetCommentForm();

    const response = await fetch(
      '/api/method/client_management.client_management.doctype.activity_comment.activity_comment.add_activity_comment',
      {
        method: 'POST',
        body: formData,
      }
    );

    const result = await response.json();

    if (result.message && result.message.success) {
      // Remove loading comment
      comments.value = comments.value.filter(c => !c.is_loading);
      
      // Add the new comment
      const newCommentData = {
        name: result.message.comment_id,
        comment: commentText,
        comment_by: window.frappe?.session?.user || 'Unknown User',
        comment_by_fullname: result.message.user_fullname,
        user_fullname: result.message.user_fullname,
        comment_date: result.message.comment_date,
        attachment: result.message.attachment_url
      };
      
      comments.value.unshift(newCommentData);
      
      // Update the latest comment ID and reset seen by for THIS NEW COMMENT only
      latestCommentId.value = result.message.comment_id;
      seenByUsers.value = []; // Clear seen by for the new comment
      
      // Show success message
      if (typeof frappe !== 'undefined' && frappe.show_alert) {
        frappe.show_alert({
          message: result.message.message || 'Comment added successfully',
          indicator: 'green'
        }, 3);
      }
      // Removed the alert() fallback
    } else {
      // Remove loading comment on error
      comments.value = comments.value.filter(c => !c.is_loading);
      
      let errorMsg = "Failed to submit comment";
      
      if (result.message && result.message.message) {
        errorMsg = result.message.message;
      } else if (result.message) {
        errorMsg = typeof result.message === 'string' ? result.message : "Server error occurred";
      }
      
      errorMessage.value = errorMsg;
      
      // Show error message using Frappe notification (no alert)
      if (typeof frappe !== 'undefined' && frappe.show_alert) {
        frappe.show_alert({
          message: errorMsg,
          indicator: 'red'
        }, 5);
      }
      // Removed the alert() fallback
    }
  } catch (error) {
    console.error("Comment submission failed:", error);
    // Remove loading comment on error
    comments.value = comments.value.filter(c => !c.is_loading);
    
    const errorMsg = error.message || "Failed to submit comment. Please try again.";
    errorMessage.value = errorMsg;
    
    // Show error message using Frappe notification (no alert)
    if (typeof frappe !== 'undefined' && frappe.show_alert) {
      frappe.show_alert({
        message: errorMsg,
        indicator: 'red'
      }, 5);
    }
    // Removed the alert() fallback
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
const handleStatusChange = async (task) => {
  if (task.status === 'Completed') {
    const confirmed = confirm('Are you sure you want to mark this task as Completed?');
    if (!confirmed) {
      task.status = previousStatus.value;
      return;
    }
  }
  await updateStatus(task);
};

const updateStatus = async (task) => {
  task.updating = true;
  
  try {
    const resource = createResource({
      url: 'client_management.client_management.doctype.activity.activity.update_activity_task_status',
      method: 'POST',
      params: {
        activity_name: task.activity_docname,
        task_name: task.name,
        status: task.status
      }
    });
    
    await resource.submit();
    await fetchTasks(); // Refresh the task list
    
    // Show success message
    if (window.frappe) {
      window.frappe.show_alert({
        message: 'Task status updated successfully',
        indicator: 'green'
      }, 3);
    }
  } catch (error) {
    console.error("Status update failed:", error);
    // Revert the status in UI
    task.status = previousStatus.value;
    if (window.frappe) {
      window.frappe.show_alert({
        message: 'Failed to update task status',
        indicator: 'red'
      }, 5);
    }
  } finally {
    task.updating = false;
  }
};

// Filter tasks
const filterTasks = () => {
  if (!searchQuery.value) {
    filteredTasks.value = [...tasks.value]
    return
  }
  
  const query = searchQuery.value.toLowerCase()
  filteredTasks.value = tasks.value.filter(task => 
    task.activity_name.toLowerCase().includes(query) ||
    task.task_name.toLowerCase().includes(query) ||
    task.priority.toLowerCase().includes(query) ||
    task.status.toLowerCase().includes(query)
  )
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
      filteredTasks.value = [...tasks.value]
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