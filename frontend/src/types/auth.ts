// src/types/auth.ts
export interface RegisterCredentials {
  organization_name: string;
  name: string;
  email: string;
  password: string;
}

export interface User {
  id: number;
  email: string;
  full_name?: string;
  role: 'admin' | 'agent';
  organization_id: number;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}