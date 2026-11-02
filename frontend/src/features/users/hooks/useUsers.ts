
import {
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'

import { userApi } from '../api/userApi'

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: userApi.list,
    staleTime: 60_000,
    retry: 1,
  })
}

export function useCreateUser() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: userApi.create,

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: ['users'],
      })
    },
  })
}
