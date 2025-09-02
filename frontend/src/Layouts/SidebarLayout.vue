<template>
  <div class="app-container">
    <Navbar @toggle-sidebar="isSidebarOpen = !isSidebarOpen" />
    <div class="content-wrapper">
      <Sidebar
        :header="header"
        :sections="visibleSections"
        :class="{ 'sidebar-collapsed': !isSidebarOpen }"
      />
      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
import Sidebar from '@/pages/Sidebar.vue';
import Navbar from '@/pages/Navbar.vue';
import { createResource } from 'frappe-ui';

export default {
  name: 'SidebarLayout',
  components: { Sidebar, Navbar },
  data() {
    return {
      isSidebarOpen: true,
      userRole: '',
      header: {
        title: 'Accsys',
        logo: '/outlook.png'
      },
      sections: [
        {
          items: [
            { label: 'Templates', to: '/templatetasks' },
            { label: 'Template Creation', to: '/template' },
            { label: 'Activities', to: '/activities' },
            { label: 'My Tasks', to: '/usertasks' },
            { label: 'Client Creation', to: '/clientcreation' }
          ]
        }
      ]
    }
  },
  computed: {
    visibleSections() {
      // If user is a Client, only show Activities and My Tasks
      if (this.userRole === 'Client') {
        return [
          {
            items: [
              { label: 'Activities', to: '/activities' },
              { label: 'My Tasks', to: '/usertasks' }
            ]
          }
        ];
      }
      
      // For other roles, show all items
      return this.sections;
    }
  },
  async mounted() {
    await this.fetchUserRole();
  },
  methods: {
    async fetchUserRole() {
      try {
        // Get current username
        const userResource = createResource({
          url: 'frappe.auth.get_logged_user'
        });
        const username = await userResource.fetch();
        
        // Then get user role profile
        const profileResource = createResource({
          url: 'frappe.client.get_value',
          params: {
            doctype: 'User',
            fieldname: 'role_profile_name',
            filters: { name: username }
          }
        });
        const profileData = await profileResource.fetch();
        console.log(profileData,"data")
        console.log(profileData.message,"message")
        
        // Set the user role
        if (profileData) {
          this.userRole = profileData.role_profile_name || '';
        }
      } catch (error) {
        console.error('Error fetching user role:', error);
        this.userRole = '';
      }
    }
  }
}
</script>

<style>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.content-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #f9fafb;
}

.sidebar {
  transition: width 0.3s ease;
}

.sidebar-collapsed {
  width: 0;
  overflow: hidden;
  padding: 0;
}
</style>