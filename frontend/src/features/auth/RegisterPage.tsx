
import { useState, type FormEvent } from 'react'
import axios from 'axios'
import { Link, useNavigate } from 'react-router-dom'
import {
  ArrowRight,
  Building2,
  LoaderCircle,
  LockKeyhole,
  Mail,
  UserRound,
} from 'lucide-react'

import { authApi } from './api/authApi'
import { useAuthStore } from '../../stores/authStore'

export function RegisterPage() {
  const navigate = useNavigate()
  const setSession = useAuthStore((state) => state.setSession)

  const [organizationName, setOrganizationName] = useState('')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const response = await authApi.register({
        organization_name: organizationName,
        name,
        email,
        password,
      })

      setSession(response.user, response.access_token)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      if (axios.isAxiosError(err)) {
        if (err.response?.status === 409) {
          setError('Este e-mail já está cadastrado.')
        } else if (err.response?.status === 429) {
          setError('Muitas tentativas de cadastro. Tente novamente mais tarde.')
        } else if (err.response?.status === 422) {
          setError('Verifique os dados informados e tente novamente.')
        } else {
          setError('Não foi possível criar sua conta.')
        }
      } else {
        setError('Ocorreu um erro inesperado.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const inputClass =
    'w-full rounded-xl border border-slate-700 bg-slate-950/60 py-3 pl-12 pr-4 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#080f1e] px-6 py-12 text-slate-100">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold tracking-tight">
            Auvren<span className="text-blue-400">.</span>
          </h1>

          <p className="mt-3 text-sm text-slate-400">
            Inteligência para transformar seu atendimento.
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-[#101a2e] p-8 shadow-2xl shadow-black/20">
          <h2 className="text-2xl font-semibold">
            Crie sua conta
          </h2>

          <p className="mt-2 text-sm text-slate-400">
            Comece a organizar seu atendimento com inteligência.
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <div>
              <label htmlFor="organization" className="mb-2 block text-sm">
                Nome da organização
              </label>
              <div className="relative">
                <Building2 size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  id="organization"
                  type="text"
                  required
                  minLength={2}
                  maxLength={150}
                  value={organizationName}
                  onChange={(event) => setOrganizationName(event.target.value)}
                  placeholder="Minha empresa"
                  className={inputClass}
                />
              </div>
            </div>

            <div>
              <label htmlFor="name" className="mb-2 block text-sm">
                Seu nome
              </label>
              <div className="relative">
                <UserRound size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  id="name"
                  type="text"
                  autoComplete="name"
                  required
                  minLength={2}
                  maxLength={150}
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  placeholder="Seu nome completo"
                  className={inputClass}
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="mb-2 block text-sm">
                E-mail
              </label>
              <div className="relative">
                <Mail size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  id="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="voce@empresa.com"
                  className={inputClass}
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="mb-2 block text-sm">
                Senha
              </label>
              <div className="relative">
                <LockKeyhole size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
                <input
                  id="password"
                  type="password"
                  autoComplete="new-password"
                  required
                  minLength={8}
                  maxLength={128}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Mínimo de 8 caracteres"
                  className={inputClass}
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
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-3 font-semibold transition hover:bg-blue-500 disabled:opacity-60"
            >
              {isLoading ? (
                <>
                  <LoaderCircle size={18} className="animate-spin" />
                  Criando conta...
                </>
              ) : (
                <>
                  Criar conta
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>

          <p className="mt-7 text-center text-sm text-slate-400">
            Já possui uma conta?{' '}
            <Link
              to="/login"
              className="font-medium text-blue-400 hover:text-blue-300"
            >
              Entrar
            </Link>
          </p>
        </div>
      </div>
    </main>
  )
}
