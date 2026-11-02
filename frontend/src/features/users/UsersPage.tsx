
import { useState, type FormEvent } from 'react'
import { AxiosError } from 'axios'
import { Plus, Users, X } from 'lucide-react'

import { useCreateUser, useUsers } from './hooks/useUsers'
import type { UserCreate } from '../../types/user'

const initialForm: UserCreate = {
  name: '',
  email: '',
  password: '',
}

export default function UsersPage() {
  const { data: users = [], isLoading, isError, refetch } = useUsers()
  const createUser = useCreateUser()

  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState<UserCreate>({ ...initialForm })
  const [formError, setFormError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError('')
    setSuccessMessage('')

    try {
      await createUser.mutateAsync(form)
      setForm({ ...initialForm })
      setShowForm(false)
      setSuccessMessage('Integrante cadastrado com sucesso!')
    } catch (error) {
      if (error instanceof AxiosError) {
        if (error.response?.status === 409) {
          setFormError('Este e-mail já está cadastrado.')
        } else if (error.response?.status === 403) {
          setFormError('Você não tem permissão para cadastrar usuários.')
        } else if (error.response?.status === 401) {
          setFormError('Sua sessão expirou. Faça login novamente.')
        } else if (error.response?.status === 422) {
          setFormError('Verifique os dados informados.')
        } else {
          setFormError('Não foi possível cadastrar o integrante.')
        }
      } else {
        setFormError('Ocorreu um erro inesperado.')
      }
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">
            Equipe
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Gerencie os integrantes da sua organização.
          </p>
        </div>

        <button
          type="button"
          onClick={() => {
            setFormError('')
            setSuccessMessage('')
            setShowForm((previous) => !previous)
          }}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
        >
          {showForm ? <X size={18} /> : <Plus size={18} />}
          {showForm ? 'Cancelar' : 'Adicionar integrante'}
        </button>
      </div>

      {successMessage && (
        <p
          role="status"
          className="rounded-lg border border-emerald-800 bg-emerald-950/30 p-4 text-sm text-emerald-400"
        >
          {successMessage}
        </p>
      )}

      {showForm && (
        <form
          onSubmit={(event) => void handleSubmit(event)}
          className="space-y-5 rounded-xl border border-slate-800 bg-slate-900 p-6"
        >
          <div>
            <h2 className="text-lg font-semibold text-white">
              Novo integrante
            </h2>
            <p className="mt-1 text-sm text-slate-400">
              Cadastre um usuário na sua organização.
            </p>
          </div>

          <div>
            <label
              htmlFor="user-name"
              className="mb-2 block text-sm text-slate-300"
            >
              Nome
            </label>
            <input
              id="user-name"
              type="text"
              required
              minLength={2}
              maxLength={150}
              autoComplete="name"
              value={form.name}
              onChange={(event) =>
                setForm({ ...form, name: event.target.value })
              }
              placeholder="Nome completo"
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label
              htmlFor="user-email"
              className="mb-2 block text-sm text-slate-300"
            >
              E-mail
            </label>
            <input
              id="user-email"
              type="email"
              required
              autoComplete="email"
              value={form.email}
              onChange={(event) =>
                setForm({ ...form, email: event.target.value })
              }
              placeholder="integrante@empresa.com"
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label
              htmlFor="user-password"
              className="mb-2 block text-sm text-slate-300"
            >
              Senha inicial
            </label>
            <input
              id="user-password"
              type="password"
              required
              minLength={8}
              maxLength={128}
              autoComplete="new-password"
              value={form.password}
              onChange={(event) =>
                setForm({ ...form, password: event.target.value })
              }
              placeholder="Mínimo de 8 caracteres"
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none focus:border-indigo-500"
            />
          </div>

          {formError && (
            <p role="alert" className="text-sm text-red-400">
              {formError}
            </p>
          )}

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={createUser.isPending}
              className="rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {createUser.isPending ? 'Cadastrando...' : 'Cadastrar integrante'}
            </button>
          </div>
        </form>
      )}

      <section className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900">
        <div className="flex items-center gap-3 border-b border-slate-800 px-5 py-4">
          <Users size={19} className="text-indigo-400" />
          <h2 className="font-semibold text-white">
            Integrantes
          </h2>
          {!isLoading && !isError && (
            <span className="ml-auto text-sm text-slate-400">
              {users.length} {users.length === 1 ? 'usuário' : 'usuários'}
            </span>
          )}
        </div>

        {isLoading ? (
          <p className="p-6 text-sm text-slate-400">
            Carregando integrantes...
          </p>
        ) : isError ? (
          <div className="space-y-3 p-6">
            <p className="text-sm text-red-400">
              Não foi possível carregar a equipe. Verifique se sua conta possui
              permissão de administrador.
            </p>
            <button
              type="button"
              onClick={() => void refetch()}
              className="rounded-lg bg-slate-700 px-4 py-2 text-sm text-white hover:bg-slate-600"
            >
              Tentar novamente
            </button>
          </div>
        ) : users.length === 0 ? (
          <p className="p-8 text-center text-sm text-slate-400">
            Nenhum integrante encontrado.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-800 bg-slate-950/50 text-slate-400">
                <tr>
                  <th className="px-5 py-4 font-medium">Integrante</th>
                  <th className="px-5 py-4 font-medium">Cargo</th>
                  <th className="px-5 py-4 font-medium">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-slate-800/50">
                    <td className="px-5 py-4">
                      <p className="font-medium text-white">{user.name}</p>
                      <p className="mt-1 text-xs text-slate-400">{user.email}</p>
                    </td>
                    <td className="px-5 py-4 text-slate-300">
                      {user.role === 'admin'
                        ? 'Administrador'
                        : user.role === 'agent'
                          ? 'Agente'
                          : user.role}
                    </td>
                    <td className="px-5 py-4">
                      <span
                        className={
                          user.is_active
                            ? 'text-emerald-400'
                            : 'text-slate-500'
                        }
                      >
                        {user.is_active ? 'Ativo' : 'Inativo'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}
