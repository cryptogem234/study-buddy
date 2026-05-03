import { Outlet, NavLink } from 'react-router-dom'

export default function Layout() {
  const navClass = ({ isActive }) =>
    `px-4 py-2 rounded-lg font-medium transition-colors ${
      isActive
        ? 'bg-brand-500 text-white'
        : 'text-slate-600 hover:bg-slate-200'
    }`

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">📚</span>
            <span className="text-xl font-bold text-brand-700">Study Buddy</span>
          </div>
          <nav className="flex gap-2">
            <NavLink to="/" end className={navClass}>Home</NavLink>
            <NavLink to="/progress" className={navClass}>Progress</NavLink>
          </nav>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8">
        <Outlet />
      </main>

      <footer className="text-center py-4 text-slate-400 text-sm">
        Keep learning, Aashi! ✨
      </footer>
    </div>
  )
}
