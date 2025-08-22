<template>
  <div class="container mx-auto p-6">
    <div v-if="loading" class="text-center py-8">
      Loading task details...
    </div>
    
    <div v-else class="space-y-6">
      <h1 class="text-2xl font-bold">{{ task.task_name }}</h1>
      
      <div class="grid grid-cols-2 gap-4 bg-white p-4 rounded-lg shadow">
        <div>
          <label class="block text-sm font-medium text-gray-700">Activity</label>
          <p class="mt-1 text-sm text-gray-900">{{ task.activity_name }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Status</label>
          <p class="mt-1 text-sm text-gray-900">{{ task.status }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">From Date</label>
          <p class="mt-1 text-sm text-gray-900">{{ formatDate(task.from_date) }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">To Date</label>
          <p class="mt-1 text-sm text-gray-900">{{ formatDate(task.to_date) }}</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Priority</label>
          <p class="mt-1 text-sm text-gray-900">{{ task.priority }}</p>
        </div>
      </div>
      
      <div class="bg-white p-4 rounded-lg shadow">
        <label class="block text-sm font-medium text-gray-700">Description</label>
        <p class="mt-1 text-sm text-gray-900 whitespace-pre-line">{{ task.description }}</p>
      </div>
      
      <!-- Comments Section -->
      <div class="grid gap-4" :class="isClient ? 'grid-cols-1' : 'grid-cols-2'">
        <!-- External Comments (visible to all) -->
        <div class="bg-white p-4 rounded-lg shadow">
          <h3 class="font-medium text-gray-700 mb-2">External Comments</h3>
          <div v-if="externalComments.length">
            <div v-for="comment in externalComments" :key="comment.name" class="mb-3 p-2 border-b">
              <p class="text-sm">{{ comment.comment }}</p>
              <p class="text-xs text-gray-500 mt-1">By {{ comment.user_fullname }} on {{ formatDate(comment.creation) }}</p>
            </div>
          </div>
          <p v-else class="text-sm text-gray-500">No external comments</p>
        </div>
        
        <!-- Internal Comments (only for non-clients) -->
        <div v-if="!isClient" class="bg-white p-4 rounded-lg shadow">
          <h3 class="font-medium text-gray-700 mb-2">Internal Comments</h3>
          <div v-if="internalComments.length">
            <div v-for="comment in internalComments" :key="comment.name" class="mb-3 p-2 border-b">
              <p class="text-sm">{{ comment.comment }}</p>
              <p class="text-xs text-gray-500 mt-1">By {{ comment.user_fullname }} on {{ formatDate(comment.creation) }}</p>
            </div>
          </div>
          <p v-else class="text-sm text-gray-500">No internal comments</p>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { createResource } from 'frappe-ui';

export default {
  setup() {
    const route = useRoute();
    const task = ref({});
    const isClient = ref(false);
    const error = ref(null);
    const taskId = ref(route.params.id);

    // Create resource for fetching task data
    const taskResource = createResource({
      url: 'client_management.client_management.doctype.activity.activity.get_task_with_comments',
      params: {
        task_id: taskId.value
      },
      auto: false,
      onSuccess(data) {
        if (data.error) {
          error.value = data.message || 'Failed to load task details';
          task.value = {};
          isClient.value = false;
        } else {
          task.value = data.task_details;
          isClient.value = data.is_client;
          error.value = null;
        }
      },
      onError(err) {
        error.value = 'Failed to load task details. Please try again.';
        console.error('API Error:', err);
        task.value = {};
        isClient.value = false;
      }
    });

    // Computed properties for comments
    const externalComments = computed(() => {
      return taskResource.data?.external_comments || [];
    });

    const internalComments = computed(() => {
      return !isClient.value ? taskResource.data?.internal_comments || [] : [];
    });

    const loading = computed(() => taskResource.loading);

    function formatDate(dateString) {
      if (!dateString) return '';
      return new Date(dateString).toLocaleDateString();
    }

    onMounted(() => {
      if (taskId.value) {
        taskResource.reload();
      } else {
        error.value = 'No task ID provided';
      }
    });

    function retry() {
      error.value = null;
      taskResource.reload();
    }

    return {
      task,
      loading,
      error,
      externalComments,
      internalComments,
      isClient,
      formatDate,
      retry,
      taskId
    };
  }
};
</script>