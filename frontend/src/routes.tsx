import { createBrowserRouter, Navigate } from 'react-router-dom'
import { Login } from './pages/Login'
import { Upload } from './pages/Upload'
import { Ask } from './pages/Ask'
import { History } from './pages/History'
import { Document } from './pages/Document'
import { Admin } from './pages/Admin'
import { App } from './App'
import { isAuthenticated, isAdmin } from './lib/auth'

function RequireAuth({ children }: { children: React.ReactNode }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

function RequireAdmin({ children }: { children: React.ReactNode }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />
  }
  if (!isAdmin()) {
    return <Navigate to="/upload" replace />
  }
  return <>{children}</>
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/upload" replace />
  },
  {
    path: '/login',
    element: <Login />
  },
  {
    path: '/',
    element: (
      <RequireAuth>
        <App />
      </RequireAuth>
    ),
    children: [
      {
        path: 'upload',
        element: <Upload />
      },
      {
        path: 'ask',
        element: <Ask />
      },
      {
        path: 'history',
        element: <History />
      },
      {
        path: 'document/:docId',
        element: <Document />
      }
    ]
  },
  {
    path: '/admin',
    element: (
      <RequireAdmin>
        <App />
      </RequireAdmin>
    ),
    children: [
      {
        index: true,
        element: <Admin />
      }
    ]
  }
])