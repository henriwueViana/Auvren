
import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'

export function AppLayout() {
  return (
    <div className="flex min-h-screen bg-[#080f1e] text-slate-100">
      <Sidebar />

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-20 shrink-0 items-center justify-between border-b border-slate-800 px-8">
          <div>
            <p className="text-xs font-medium uppercase tracking-widest text-blue-400">
              Workspace
            </p>
            <h1 className="text-lg font-semibold">
              Painel de controle
            </h1>
          </div>

          <div className="flex h-9 w-9 items-center justify-center rounded-full border border-blue-500/30 bg-blue-500/10 text-sm font-semibold text-blue-400">
            A
          </div>
        </header>

        <main className="flex-1 p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
