// Axios instance with JWT interceptor
// TODO: Wire up base URL from env, attach Bearer token, handle 401 refresh
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});
