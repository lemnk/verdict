import { Link, useNavigate } from 'react-router-dom'
import { getUser, logout } from '../lib/auth'
import { Button } from './ui/Button'

export function NavBar() {
  const user = getUser()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  if (!user) {
    return null
  }

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/upload" className="text-xl font-bold text-gray-900">
              VerdictVault
            </Link>
            <div className="ml-10 flex items-baseline space-x-4">
              <Link
                to="/upload"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                Upload
              </Link>
              <Link
                to="/ask"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                Ask
              </Link>
              <Link
                to="/history"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                History
              </Link>
            </div>
          </div>
          
          <div className="flex items-center">
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Welcome, {user.name}
              </span>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}