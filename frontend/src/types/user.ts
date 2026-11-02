
export interface OrganizationUser {
  id: number
  organization_id: number
  name: string
  email: string
  role: string
  is_active: boolean
}

export interface UserCreate {
  name: string
  email: string
  password: string
}
