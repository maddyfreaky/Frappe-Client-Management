<template>
  <div class="p-6">
    <!-- Search and Sort Bar -->
    <div class="mb-4 flex flex-col sm:flex-row sm:items-center gap-3">
      <!-- Search -->
      <div class="flex-1 w-full">
        <Input
          type="text"
          placeholder="Search templates..."
          v-model="searchQuery"
          class="w-full"
        >
          <template #prefix>
            <SearchIcon class="h-4 w-4" />
          </template>
        </Input>
      </div>

      <!-- Sort -->
      <div class="w-full sm:w-auto">
        <Dropdown :options="sortOptions" v-model="sortField">
          <template #default="{ open }">
            <Button variant="outline" class="w-full sm:w-auto">
              <span class="flex items-center gap-2">
                <ArrowUpDownIcon class="h-4 w-4" />
                Sort: {{ currentSortLabel }}
                <SortIndicator :active="true" :direction="sortDirection" />
              </span>
            </Button>
          </template>
        </Dropdown>
      </div>
    </div>

    
    <div class="border rounded-lg overflow-hidden overflow-x-auto">
      
      <div class="grid grid-cols-12 text-xs text-gray-700 uppercase tracking-wider bg-muted p-3 border-b font-semibold">
        <div class="col-span-4 flex items-center gap-2 cursor-pointer" @click="setSort('template_name')">
          Template Name
          <SortIndicator :active="sortField === 'template_name'" :direction="sortDirection" />
        </div>
        <div class="col-span-3 flex items-center gap-2 cursor-pointer" @click="setSort('owner')">
          Created By
          <SortIndicator :active="sortField === 'owner'" :direction="sortDirection" />
        </div>
        <div class="col-span-3 flex items-center gap-2 cursor-pointer" @click="setSort('creation')">
          Created At
          <SortIndicator :active="sortField === 'creation'" :direction="sortDirection" />
        </div>
        <div class="col-span-2 text-right">Actions</div>
      </div>

      
      <div v-if="templatesResource.loading" class="p-8 text-center">
        Loading templates...
      </div>
      <div v-else-if="filteredTemplates.length > 0">
        <div 
          v-for="template in paginatedTemplates" 
          :key="template.name"
          class="grid grid-cols-12 gap-4 p-3 border-b text-sm hover:bg-accent/20 transition"
        >
          <div class="col-span-4 font-medium truncate">{{ template.template_name }}</div>
          <div class="col-span-3">{{ getUsername(template.owner) }}</div>
          <div class="col-span-3">{{ formatDate(template.creation) }}</div>
          <div class="col-span-2 flex justify-end gap-2">
            <Button icon="edit" size="sm" @click="editTemplate(template.name)" />
<Button 
  icon="trash-2" 
  size="sm" 
  @click="deleteTemplate(template.name, template.template_name || template.title || 'this template')" 
/>             <Button 
            @click="assignTemplate(template.name)" 
            size="sm" 
            variant="outline"
          >
            Assign
          </Button>
          </div>
        </div>
      </div>
      <div v-else class="p-8 text-center text-gray-500">
        No templates found
      </div>

      
      <div v-if="filteredTemplates.length > 0" class="flex items-center justify-between p-3 border-t bg-gray-50 text-sm">
        <div class="text-gray-600">
          Showing {{ startItem }}–{{ endItem }} of {{ filteredTemplates.length }} templates
        </div>
        <div class="flex gap-1">
          <Button @click="prevPage" :disabled="currentPage === 1" variant="outline" size="sm">Previous</Button>
          <Button
            v-for="page in visiblePages"
            :key="page"
            @click="goToPage(page)"
            :variant="currentPage === page ? 'solid' : 'outline'"
            size="sm"
          >
            {{ page }}
          </Button>
          <Button @click="nextPage" :disabled="currentPage === totalPages" variant="outline" size="sm">Next</Button>
        </div>
        <div class="flex items-center gap-2">
          <span>Rows per page:</span>
          <select v-model="pageSize" @change="resetPagination" class="border rounded px-2 py-1 text-sm">
            <option v-for="size in pageSizes" :key="size" :value="size">{{ size }}</option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Button, createResource, Input, Dropdown } from 'frappe-ui'
import { useRouter } from 'vue-router'

const router = useRouter()
const userMap = ref({})
const assignTemplate = (templateName) => {
  router.push({
    name: 'ActivityForm',
    params: { templateName: templateName }
  })
}

// Update the editTemplate method to navigate to the new editor page
const editTemplate = (name) => {
  router.push({ name: 'TemplateEditor', params: { name } })
}



const SearchIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>`
}
const ArrowUpDownIcon = {
  template: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" /></svg>`
}


const SortIndicator = {
  props: ['active', 'direction'],
  template: `
    <span class="ml-1">
      <svg v-if="active" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path v-if="direction === 'asc'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
        <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </span>
  `
}


const templates = ref([])
const searchQuery = ref('')
const sortField = ref('creation')
const sortDirection = ref('desc')
const currentPage = ref(1)
const pageSize = ref(10)
const pageSizes = [5, 10, 20, 50]


const sortOptions = [
  { label: 'Name', value: 'template_name' },
  { label: 'Created By', value: 'owner' },
  { label: 'Created Date', value: 'creation' }
]

const currentSortLabel = computed(() => {
  const option = sortOptions.find(opt => opt.value === sortField.value)
  return option ? option.label : 'Custom'
})

// Filter + sort + paginate
const filteredTemplates = computed(() => {
  let result = [...templates.value]
  const query = searchQuery.value.toLowerCase()

  if (query) {
    result = result.filter(t =>
      t.template_name.toLowerCase().includes(query) ||
      t.owner.toLowerCase().includes(query)
    )
  }

  if (sortField.value) {
    result.sort((a, b) => {
      let valA = a[sortField.value]
      let valB = b[sortField.value]
      if (valA > valB) return sortDirection.value === 'asc' ? 1 : -1
      if (valA < valB) return sortDirection.value === 'asc' ? -1 : 1
      return 0
    })
  }

  return result
})

const totalPages = computed(() => Math.ceil(filteredTemplates.value.length / pageSize.value))
const startItem = computed(() => (currentPage.value - 1) * pageSize.value + 1)
const endItem = computed(() => Math.min(currentPage.value * pageSize.value, filteredTemplates.value.length))
const paginatedTemplates = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredTemplates.value.slice(start, start + pageSize.value)
})

const visiblePages = computed(() => {
  const pages = []
  const max = 5
  let start = Math.max(1, currentPage.value - Math.floor(max / 2))
  let end = Math.min(start + max - 1, totalPages.value)
  if (end - start < max - 1) start = Math.max(1, end - max + 1)
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})


const getUsername = (email) => {
  if (!email) return 'Unknown'
  return userMap.value[email]?.username || email.split('@')[0]
}

const fetchUserData = async () => {
  const userResource = createResource({
    url: 'frappe.client.get_list',
    params: {
      doctype: 'User',
      fields: ['email', 'username'],
      limit: 0
    },
    auto: true,
    onSuccess(data) {
      // Create a mapping of email to username
      const mapping = {}
      data.forEach(user => {
        mapping[user.email] = {
          username: user.username
        }
      })
      userMap.value = mapping
    },
    onError(error) {
      console.error('Error fetching user data:', error)
    }
  })
}

onMounted(() => {
  fetchUserData()
})

// Load data
const templatesResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Template',
    fields: ['name', 'template_name', 'owner', 'creation'],
    limit: 0
  },
  auto: true,
  onSuccess(data) {
    templates.value = data
  },
  onError(error) {
    console.error('Fetch error:', error)
  }
})


const formatDate = date => new Date(date).toLocaleDateString()


const deleteTemplate = async (name, displayName) => {
  // Show confirmation with the template's display name
  const userConfirmed = confirm(`Are you sure you want to delete "${displayName}"?`);
  
  if (userConfirmed) {
    const res = createResource({
      url: 'frappe.client.delete',
      params: { doctype: 'Template', name }  // Still uses the docname for deletion
    });
    await res.submit();
    templatesResource.reload();
  }
};


const setSort = field => {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'asc'
  }
  currentPage.value = 1
}
const resetPagination = () => (currentPage.value = 1)
const prevPage = () => currentPage.value > 1 && currentPage.value--
const nextPage = () => currentPage.value < totalPages.value && currentPage.value++
const goToPage = page => (currentPage.value = page)

// Reset pagination on search
watch(searchQuery, () => {
  currentPage.value = 1
})
</script>

<style scoped>
select {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
}
</style>
