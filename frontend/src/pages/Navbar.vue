<template>

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
  <nav class="navbar">
    <div class="navbar-content">
      <!-- Left section -->
      <div class="navbar-section">
        <div class="sidebar-header">
      <div class="header-content">
        
        <h1><b>Accsys</b></h1>
      </div>
    </div>
        <!-- <div class="breadcrumbs">Dashboard</div> -->
      </div>
     
      <!-- Right section -->
      <div class="navbar-section">
        <div class="user-menu">
          <div class="notifications">
            <svg width="20" height="20" viewBox="0 0 24 24">
              <path fill="currentColor" d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.89 2 2 2zm6-6v-5c0-3.07-1.64-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.63 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z"/>
            </svg>
            <span class="badge">3</span>
          </div>
         
          <div class="user-avatar-container" ref="container">
            <div class="user-avatar" @click="toggleMenu">
              
<i class="fa-solid fa-user text-4xl text-gray-600"></i>
            </div>
           
            <div v-if="showMenu" class="logout-menu">
              <ul>
                <li @click="handleLogout">Logout</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>
 
<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { session } from '../data/session';
 
const showMenu = ref(false);
const container = ref(null);
 
const toggleMenu = (e) => {
  e.stopPropagation();
  showMenu.value = !showMenu.value;
};
 
const handleLogout = () => {
  // Close the menu first
  showMenu.value = false;
  // Trigger the existing logout functionality
  session.logout.submit();
};
 
const handleClickOutside = (event) => {
  if (container.value && !container.value.contains(event.target)) {
    showMenu.value = false;
  }
};
 
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});
 
onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>
 
<style scoped>
.navbar {
  height: 60px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  padding: 0 20px;
}
 
.navbar-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
 
.navbar-section {
  display: flex;
  align-items: center;
  gap: 20px;
}
 
.menu-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  color: #4b5563;
}
 
.menu-button:hover {
  background: #f3f4f6;
}
 
.breadcrumbs {
  font-size: 14px;
  color: #4b5563;
  font-weight: 500;
}
 
.search-bar {
  position: relative;
  width: 240px;
}
 
.search-bar input {
  width: 100%;
  padding: 8px 12px 8px 32px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  font-size: 14px;
}
 
.search-bar svg {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
}
 
.user-menu {
  display: flex;
  align-items: center;
  gap: 16px;
}
 
.notifications {
  position: relative;
  cursor: pointer;
}
 
.badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #ef4444;
  color: white;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}
 
.user-avatar-container {
  position: relative;
  display: inline-block;
}
 
.user-avatar {
  cursor: pointer;
}
 
.user-avatar img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}
 
.logout-menu {
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: 5px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  z-index: 100;
  min-width: 120px;
}
 
.logout-menu ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
 
.logout-menu li {
  padding: 8px 16px;
  cursor: pointer;
}
 
.logout-menu li:hover {
  background-color: #f5f5f5;
}
</style>
 