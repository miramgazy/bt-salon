import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/auth/LoginView.vue')
  },
  {
    path: '/',
    component: () => import('../components/layout/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '/admin',
        name: 'Dashboard',
        component: () => import('../views/admin/DashboardView.vue')
      },
      {
        path: 'admin/calendar',
        name: 'calendar',
        component: () => import('../views/admin/CalendarView.vue')
      },
      {
        path: '/admin/appointments',
        name: 'Appointments',
        component: () => import('../views/admin/AppointmentsView.vue')
      },
      {
        path: '/admin/clients',
        name: 'Clients',
        component: () => import('../views/admin/ClientsView.vue')
      },
      {
        path: 'admin/shifts',
        name: 'shifts',
        component: () => import('../views/admin/ShiftsView.vue')
      },
      {
        path: '/admin/expenses',
        name: 'Expenses',
        component: () => import('../views/admin/ExpensesView.vue')
      },
      {
        path: 'superadmin/masters',
        name: 'masters',
        component: () => import('../views/superadmin/MastersView.vue')
      },
      {
        path: 'superadmin/organization',
        name: 'organization',
        component: () => import('../views/superadmin/OrganizationView.vue')
      },
      {
        path: 'superadmin/services',
        name: 'services',
        component: () => import('../views/superadmin/ServicesView.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
