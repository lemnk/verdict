const TOKEN_KEY = 'verdictvault_token'
const USER_KEY = 'verdictvault_user'

export interface User {
  id: number
  email: string
  name: string
  role: string
}

export const setToken = (token: string): void => {
  localStorage.setItem(TOKEN_KEY, token)
}

export const getToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY)
}

export const removeToken = (): void => {
  localStorage.removeItem(TOKEN_KEY)
}

export const setUser = (user: User): void => {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export const getUser = (): User | null => {
  const userStr = localStorage.getItem(USER_KEY)
  if (!userStr) return null
  
  try {
    return JSON.parse(userStr)
  } catch {
    return null
  }
}

export const removeUser = (): void => {
  localStorage.removeItem(USER_KEY)
}

export const isAuthenticated = (): boolean => {
  return getToken() !== null
}

export const isAdmin = (): boolean => {
  const user = getUser()
  return user?.role === 'admin'
}

export const logout = (): void => {
  removeToken()
  removeUser()
}