import api from '@/api'

// Updated to match the new Multi-bot Discovery structure
const BASE = '/accounts/tma'

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {}
}

/**
 * Get current user profile from /api/accounts/tma/me/
 */
async function getProfile(token) {
  const res = await api.get(`${BASE}/me/`, { headers: authHeaders(token) })
  return res.data
}

/**
 * Update current user profile using TMA endpoint
 */
async function updateProfile(token, data) {
  const res = await api.patch(`${BASE}/me/`, data, { headers: authHeaders(token) })
  return res.data
}

export default {
  getProfile,
  updateProfile
}
