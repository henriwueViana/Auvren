
import { useState, type FormEvent } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, LockKeyhole, Mail, LoaderCircle } from 'lucide-react'

import { authApi } from './api/authApi'
import { useAuthStore } from '../../stores/authStore'

export function LoginPage() {
  const navigate = useNavigate()
  const setSession = useAuthStore((state) => state.setSession)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const response = await authApi.login({ email, password })

      setSession(response.user, response.access_token)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 401) {
          setError('E-mail ou senha inválidos.')
        } else if (err.response?.status === 429) {
          setError('Muitas tentativas. Aguarde um minuto.')
        } else {
          setError('Não foi possível entrar. Tente novamente.')
        }
      } else {
        setError('Ocorreu um erro inesperado.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#080f1e] px-6 py-12 text-slate-100">
      <div className="w-full max-w-md">
        <div className="mb-10 text-center">
          <div className="mb-3 inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-500/10 text-blue-400">
            <LockKeyhole size={27} />
          </div>

          <h1 className="text-4xl font-bold tracking-tight">
            Auvren<span className="text-blue-400">.</span>
          </h1>

          <p className="mt-3 text-sm text-slate-400">
            Inteligência para transformar seu atendimento.
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-[#101a2e] p-8 shadow-2xl shadow-black/20">
          <h2 className="text-2xl font-semibold tracking-tight">
            Bem-vindo de volta
          </h2>

          <p className="mt-2 text-sm text-slate-400">
            Entre na sua conta para acessar o painel.
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <div>
              <label htmlFor="email" className="mb-2 block text-sm font-medium">
                E-mail
              </label>

              <div className="relative">
                <Mail
                  size={18}
                  className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
                />
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="voce@empresa.com"
                  className="w-full rounded-xl border border-slate-700 bg-slate-950/60 py-3 pl-12 pr-4 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="mb-2 block text-sm font-medium">
                Senha
              </label>

              <div className="relative">
                <LockKeyhole
                  size={18}
                  className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
                />
                <input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Digite sua senha"
                  className="w-full rounded-xl border border-slate-700 bg-slate-950/60 py-3 pl-12 pr-4 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
                />
              </div>
            </div>

            {error && (
              <p role="alert" className="text-sm text-red-400">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-3 font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isLoading ? (
                <>
                  <LoaderCircle size={18} className="animate-spin" />
                  Entrando...
                </>
              ) : (
                <>
                  Entrar no Auvren
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>
        </div>

        <p className="mt-8 text-center text-xs text-slate-500">
          © {new Date().getFullYear()} Auvren. Todos os direitos reservados.
        </p>
      </div>
    </main>
  )
}
