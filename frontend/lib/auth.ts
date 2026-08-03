// JWT decode helpers and RBAC role checks
// TODO: Implement decodeToken, hasRole, getCurrentUser
export const ROLES = {
  OPERATOR: 'operator',
  MAINTENANCE: 'maintenance',
  MANAGER: 'manager',
} as const;

export type Role = (typeof ROLES)[keyof typeof ROLES];
