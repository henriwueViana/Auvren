
import { api } from '../../../lib/api'

import type {
  OrganizationUser,
  UserCreate,
} from '../../../types/user'

export const userApi = {
  async list(): Promise<OrganizationUser[]> {
    const response = await api.get<OrganizationUser[]>(
      '/api/v1/users'
    )

    return response.data
  },

  async create(data: UserCreate): Promise<OrganizationUser> {
    const response = await api.post<OrganizationUser>(
      '/api/v1/users',
      data
    )

    return response.data
  },
}
