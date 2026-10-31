// src/api/auth.ts
import { apiClient } from './client';
import type { AuthResponse, RegisterCredentials } from '../types/auth';

interface LoginCredentials {
  email: string;
  password: string;
}

export const loginUser = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
  return response.data;
};

export const registerUser = async (credentials: RegisterCredentials): Promise<AuthResponse> => {
  // Ajuste o endpoint '/auth/register' caso no seu backend a rota tenha outro nome
  const response = await apiClient.post<AuthResponse>('/auth/register', credentials);
  return response.data;
};