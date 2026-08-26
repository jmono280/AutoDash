import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import axios from 'axios'
import { useAuthStore } from '@/store/authStore'
import { useChangePassword } from '@/viewmodels/useAuth'
import Spinner from '@/components/ui/Spinner'

const schema = z
  .object({
    current_password: z.string().min(1, 'La contraseña actual es requerida'),
    new_password: z
      .string()
      .min(8, 'La nueva contraseña debe tener al menos 8 caracteres')
      .regex(/[A-Z]/, 'Debe contener al menos una mayúscula')
      .regex(/\d/, 'Debe contener al menos un número')
      .regex(/[!@#$%^&*(),.?":{}|<>_\-=+\[\];'/\\`~]/, 'Debe contener al menos un signo de puntuación'),
    confirm_password: z.string().min(1, 'Confirma la nueva contraseña'),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: 'Las contraseñas no coinciden',
    path: ['confirm_password'],
  })
  .refine((data) => data.current_password !== data.new_password, {
    message: 'La nueva contraseña debe ser diferente a la actual',
    path: ['new_password'],
  })

type FormData = z.infer<typeof schema>

export default function ProfileView() {
  const user = useAuthStore((s) => s.user)
  const { mutate, isPending, isSuccess } = useChangePassword()
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<FormData>({ resolver: zodResolver(schema) })

  function onSubmit(data: FormData) {
    setServerError(null)
    mutate(
      {
        current_password: data.current_password,
        new_password: data.new_password,
      },
      {
        onSuccess: () => reset(),
        onError: (err) => {
          if (axios.isAxiosError(err)) {
            const detail = (err.response?.data as { detail?: string })?.detail
            setServerError(detail ?? 'No se pudo actualizar la contraseña.')
          } else {
            setServerError('Ocurrió un error inesperado.')
          }
        },
      },
    )
  }

  return (
    <div className="max-w-xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Perfil</h1>
      <p className="text-sm text-gray-500 mb-8">{user?.full_name ?? user?.email}</p>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Cambiar contraseña</h2>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
          <div>
            <label htmlFor="current_password" className="block text-sm font-medium text-gray-700 mb-1">
              Contraseña actual
            </label>
            <input
              id="current_password"
              type="password"
              autoComplete="current-password"
              {...register('current_password')}
              className={`w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#ffea00] transition-shadow ${
                errors.current_password ? 'border-red-400 bg-red-50' : 'border-gray-300'
              }`}
            />
            {errors.current_password && (
              <p className="mt-1 text-xs text-red-600">{errors.current_password.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="new_password" className="block text-sm font-medium text-gray-700 mb-1">
              Nueva contraseña
            </label>
            <input
              id="new_password"
              type="password"
              autoComplete="new-password"
              {...register('new_password')}
              className={`w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#ffea00] transition-shadow ${
                errors.new_password ? 'border-red-400 bg-red-50' : 'border-gray-300'
              }`}
            />
            {errors.new_password && (
              <p className="mt-1 text-xs text-red-600">{errors.new_password.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 mb-1">
              Confirmar nueva contraseña
            </label>
            <input
              id="confirm_password"
              type="password"
              autoComplete="new-password"
              {...register('confirm_password')}
              className={`w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#ffea00] transition-shadow ${
                errors.confirm_password ? 'border-red-400 bg-red-50' : 'border-gray-300'
              }`}
            />
            {errors.confirm_password && (
              <p className="mt-1 text-xs text-red-600">{errors.confirm_password.message}</p>
            )}
          </div>

          {serverError && (
            <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
              {serverError}
            </div>
          )}

          {isSuccess && (
            <div className="rounded-lg bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-700">
              Contraseña actualizada correctamente.
            </div>
          )}

          <button
            type="submit"
            disabled={isPending}
            className="w-full flex items-center justify-center gap-2 rounded-lg bg-[#ffea00] px-4 py-2.5 text-sm font-semibold text-gray-900 hover:bg-yellow-400 focus:outline-none focus:ring-2 focus:ring-[#ffea00] focus:ring-offset-2 disabled:opacity-60 transition-colors"
          >
            {isPending && <Spinner size="sm" className="w-4 h-4" />}
            {isPending ? 'Guardando…' : 'Cambiar contraseña'}
          </button>
        </form>
      </div>
    </div>
  )
}
