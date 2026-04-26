import { defineStore } from 'pinia'
import api from '@/api'
import axios from 'axios'
import usersService from '../services/users.service'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    organizationId: localStorage.getItem('org_id') || null,
    organizationName: null,
    organizationSettings: null,
    role: null,
    activeRole: localStorage.getItem('tma_active_role') || null,
    user: null,
    loading: true,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    // Physical role checks (Hierarchy)
    isOwner: (state) => state.role === 'owner',
    isAdmin: (state) => state.role === 'owner' || state.role === 'admin',
    isMaster: (state) => state.role === 'owner' || state.role === 'admin' || state.role === 'master' || !!state.user?.has_master_profile,
    
    currentRole: (state) => state.activeRole || state.role,
    isOnboarded: (state) => {
      if (state.role === 'admin' || state.role === 'owner' || state.role === 'master') return true
      return !!(state.user?.phone || state.user?.is_onboarded)
    },
    needsConsent: (state) => state.user?.is_bot_subscribed == null
  },

  actions: {
    setRoleMode(mode) {
      this.activeRole = mode
      localStorage.setItem('tma_active_role', mode)
    },
    async login(initData, organizationId) {
      this.loading = true
      this.error = null
      try {
        // Updated to matching backend's new TmaAuthView endpoint
        // Fixed: removed redundant /api (it's already in base baseURL)
        const response = await api.post('/accounts/tma/auth/', {
          initData,
          organization_id: organizationId
        })

        const { access, refresh, user, organization_settings } = response.data

        this.token = access
        this.refreshToken = refresh

        // Extract from nested user object
        this.user = user
        this.role = user.role
        this.organizationId = user.organization_id
        this.organizationName = user.organization_name
        this.organizationSettings = organization_settings || null

        // We do not reset activeRole here anymore to allow role persistence


        // Persist
        localStorage.setItem('access_token', access)
        localStorage.setItem('refresh_token', refresh)
        localStorage.setItem('org_id', user.organization_id)
        localStorage.setItem('tma_role', user.role)
        localStorage.setItem('tma_user', JSON.stringify(user))
        if (organization_settings) {
          localStorage.setItem('tma_org_settings', JSON.stringify(organization_settings))
        }

        // Setup axios default header
        axios.defaults.headers.common['Authorization'] = `Bearer ${access}`

        return true
      } catch (err) {
        this.error = err.response?.data?.error || 'Authentication failed'
        return false
      } finally {
        this.loading = false
      }
    },

    async refreshTokenAction() {
      if (!this.refreshToken) return false
      try {
        const response = await axios.post('/api/accounts/token/refresh/', {
          refresh: this.refreshToken
        })
        const { access } = response.data
        this.token = access
        localStorage.setItem('access_token', access)
        axios.defaults.headers.common['Authorization'] = `Bearer ${access}`
        return true
      } catch (err) {
        this.logout()
        return false
      }
    },

    async updateProfile(data) {
      this.error = null
      try {
        const responseData = await usersService.updateProfile(this.token, data)
        const updatedUser = responseData.user || responseData

        // If a merge happened, backend returns new tokens
        if (responseData.access && responseData.refresh) {
          this.token = responseData.access
          this.refreshToken = responseData.refresh
          localStorage.setItem('access_token', responseData.access)
          localStorage.setItem('refresh_token', responseData.refresh)
          axios.defaults.headers.common['Authorization'] = `Bearer ${responseData.access}`
        }

        this.user = updatedUser
        this.role = updatedUser.role || this.role
        if (this.role) localStorage.setItem('tma_role', this.role)

        return updatedUser
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to update profile'
        throw err
      }
    },

    async fetchOrganizationSettings() {
      try {
        const response = await api.get('/organization/settings/')
        this.organizationSettings = response.data
        localStorage.setItem('tma_org_settings', JSON.stringify(response.data))
        return response.data
      } catch (err) {
        console.error('fetchOrganizationSettings error:', err)
      }
    },
    async fetchCurrentUser() {
      if (!this.token) return
      try {
        const response = await api.get('/accounts/tma/me/')
        const data = response.data

        this.user = data
        this.role = data.role

        if (data.organization_settings) {
          this.organizationSettings = data.organization_settings
          localStorage.setItem('tma_org_settings', JSON.stringify(data.organization_settings))
        }
        localStorage.setItem('tma_role', data.role)
        localStorage.setItem('tma_user', JSON.stringify(data))
      } catch (err) {
        console.error('fetchCurrentUser error:', err)
        if (err.response?.status === 401 && this.refreshToken) {
          const ok = await this.refreshTokenAction()
          if (ok) return this.fetchCurrentUser()
        }
        this.logout()
      }
    },

    restoreAuth() {
      const token = localStorage.getItem('access_token')
      const refresh = localStorage.getItem('refresh_token')
      if (token) {
        this.token = token
        this.refreshToken = refresh
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

        try {
          const userStr = localStorage.getItem('tma_user')
          if (userStr) {
            this.user = JSON.parse(userStr)
            this.role = this.user.role
          }
          const orgSettingsStr = localStorage.getItem('tma_org_settings')
          if (orgSettingsStr) {
            this.organizationSettings = JSON.parse(orgSettingsStr)
          }
        } catch (e) {
          console.warn('Error parsing cached user/settings', e)
        }
      }
    },

    logout() {
      this.token = null
      this.refreshToken = null
      this.organizationId = null
      this.organizationName = null
      this.role = null
      this.user = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('org_id')
      localStorage.removeItem('tma_role')
      localStorage.removeItem('tma_user')
      localStorage.removeItem('tma_org_settings')
      delete axios.defaults.headers.common['Authorization']
    }
  }
})
