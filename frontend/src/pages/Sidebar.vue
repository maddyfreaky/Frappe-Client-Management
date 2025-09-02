 
 
<template>
  <div class="sidebar">
    <!-- Header section with aligned logo and title -->
    <!-- <div class="sidebar-header">
      <div class="header-content">
        <img :src="header.logo" alt="Logo" class="logo" v-if="header.logo" />
        <h2>{{ header.title }}</h2>
      </div>
    </div> -->
   
    <!-- Navigation sections -->
    <div class="sidebar-sections">
      <div v-for="(section, index) in sections" :key="index" class="section">
        <div class="section-items">
          <router-link
            v-for="item in section.items"
            :key="item.label"
            :to="item.to"
            custom
            v-slot="{ navigate, isActive }"
          >
            <div
              @click="navigate"
              :class="['nav-item', { 'active-route': isActive }]"
            >
              <span class="item-label">{{ item.label }}</span>
            </div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>
 
<script>
export default {
  name: 'Sidebar',
  props: {
    header: {
      type: Object,
      required: true
    },
    sections: {
      type: Array,
      required: true
    }
  }
}
</script>
 
<style scoped>
.sidebar {
  width: 260px;
  height: 100vh;
  background: #fff;
  border-right: 1px solid #e5e7eb;
  padding: 20px 0;
  font-family: 'Inter', sans-serif;
}
 
/* Header with aligned logo and title */
.sidebar-header {
  padding: 16px 20px;
  border-bottom: 1px solid #f3f4f6;
  margin-bottom: 16px;
}
 
.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}
 
.logo {
  height: 40px;
  width: auto;
}
 
.sidebar-header h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: #111827;
  white-space: nowrap;
}
 
/* Navigation items */
.section-items {
  padding: 8px 0;
}
 
.nav-item {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  cursor: pointer;
  color: #374151;
  font-size: 14px;
  transition: all 0.2s ease;
}
 
.nav-item:hover {
  background: #f9fafb;
}
 
.active-route {
  background: #f3f4f6;
  color: #111827;
  font-weight: 500;
  border-left: 3px solid #3b82f6;
}
 
.item-label {
  flex: 1;
}
</style>
 