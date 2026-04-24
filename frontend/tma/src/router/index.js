import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/onboarding/welcome',
    name: 'welcome',
    component: () => import('../views/onboarding/WelcomeView.vue')
  },
  {
    path: '/onboarding/phone',
    name: 'phone',
    component: () => import('../views/onboarding/PhoneInputView.vue')
  },
  {
    path: '/onboarding/consent',
    name: 'consent',
    component: () => import('../views/onboarding/BotConsentView.vue')
  },

  {
    path: '/master',
    component: () => import('../components/layout/MasterLayout.vue'),
    meta: { role: 'master' },
    children: [
      {
        path: '',
        name: 'master-home',
        component: () => import('../views/master/MasterHomeView.vue')
      },
      {
        path: 'bookings',
        name: 'master-bookings',
        component: () => import('../views/master/MasterBookingsView.vue')
      },
      {
        path: 'income',
        name: 'master-income',
        component: () => import('../views/master/MasterIncomeView.vue')
      },
      {
        path: 'profile',
        name: 'master-profile',
        component: () => import('../views/master/MasterProfileView.vue')
      }
    ]
  },

  {
    path: '/',
    component: () => import('../components/layout/TmaLayout.vue'),
    meta: { role: 'client' },
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('../views/HomeView.vue')
      },
      {
        path: 'tma-appointments',
        name: 'appointments',
        component: () => import('../views/MyAppointments.vue')
      },
      {
        path: 'profile',
        name: 'profile',
        component: () => import('../views/ProfileView.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory('/tma/'),
  routes
})

// Security Guard: Prevent mixing modules
router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()
  
  // Skip role-based guarding if still initializing or if on onboarding
  if (auth.loading || to.path.startsWith('/onboarding')) {
    return next()
  }

  const roleRequired = to.matched.find(record => record.meta.role)?.meta.role
  
  if (roleRequired && auth.isAuthenticated) {
    const currentRole = auth.currentRole
    
    // Only redirect if a definite role mismatch is detected
    if (roleRequired === 'master' && currentRole === 'client') {
      return next('/')
    }
    if (roleRequired === 'client' && currentRole === 'master') {
      return next('/master')
    }
  }

  next()
})

export default router
