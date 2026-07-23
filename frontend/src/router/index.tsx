import { createBrowserRouter, Navigate } from 'react-router-dom'
import Login from '../pages/Login'
import Dashboard from '../pages/Dashboard'
import Users from '../pages/Users'
import Profiles from '../pages/Profiles'
import Containers from '../pages/Containers'
import Settings from '../pages/Settings'
import ProtectedRoute from '../components/common/ProtectedRoute'
import AppLayout from '../components/layout/AppLayout'

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: 'dashboard', element: <Dashboard /> },
      { path: 'users', element: <Users /> },
      { path: 'profiles', element: <Profiles /> },
      { path: 'containers', element: <Containers /> },
      { path: 'settings', element: <Settings /> },
    ],
  },
])
