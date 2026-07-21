import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Topbar from './Topbar'

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <div className="min-h-screen bg-bg-primary">
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(!collapsed)} />
      <div className={`transition-all duration-200 ${collapsed ? 'ml-14' : 'ml-52'}`}>
        <Topbar />
        <main className="p-4 animate-fade-in">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
