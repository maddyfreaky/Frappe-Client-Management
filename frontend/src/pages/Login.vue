<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-4">
    <!-- Header section -->
    <header class="text-center mb-8">
      <h1 class="text-3xl font-bold text-gray-800 mb-2">Imprints</h1>
      
    </header>

    <!-- Login card -->
    <Card title="Welcome!" class="w-full max-w-md mt-4">
      <form class="flex flex-col space-y-4 w-full" @submit.prevent="submit">
        <Input
          required
          name="email"
          type="text"
          placeholder="johndoe@email.com"
          label="User ID"
          v-model="email"
        />
        
        <div class="relative">
          <Input
            required
            name="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="••••••"
            label="Password"
            v-model="password"
          />
          <button
            type="button"
            class="absolute right-2 top-7 text-gray-500 hover:text-gray-700"
            @click="togglePasswordVisibility"
          >
            <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
            </svg>
          </button>
        </div>
        
        <Button :loading="session.login.loading" variant="solid" class="w-full">
          Login
        </Button>
      </form>
    </Card>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { Card, Input, Button, toast } from 'frappe-ui'
import { session } from "../data/session"

const email = ref('')
const password = ref('')
const showPassword = ref(false)

function togglePasswordVisibility() {
  showPassword.value = !showPassword.value
}

async function submit(e) {
  const formData = new FormData(e.target)
  
  try {
    await session.login.submit({
      email: formData.get("email"),
      password: formData.get("password"),
    })
    
    // Show success alert
    if (typeof Swal !== 'undefined') {
      Swal.fire({
        title: 'success',
        icon: 'success',
        showConfirmButton: false,
        timer : 1500,
        toast : true,
        position : 'top-end'
      })
    } else {
      alert('Login successful!')
    }
    
  } catch (error) {
    // Show error alert
    if (typeof Swal !== 'undefined') {
      Swal.fire({
        title: 'Login Failed',
        text: 'Invalid email or password. Please try again.',
        icon: 'error',
        confirmButtonText: 'Try Again'
      })
    } else {
      alert('Login failed. Invalid email or password.')
    }
  }
}

// Load SweetAlert from CDN
onMounted(() => {
  if (typeof Swal === 'undefined') {
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/sweetalert2@11'
    script.onload = () => {
      console.log('SweetAlert2 loaded from CDN')
    }
    document.head.appendChild(script)
    
    const link = document.createElement('link')
    link.rel = 'stylesheet'
    link.href = 'https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.min.css'
    document.head.appendChild(link)
  }
})
</script>
