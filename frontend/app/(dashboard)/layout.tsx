// Dashboard shell layout — wraps all authenticated dashboard pages
// TODO: Add sidebar, topbar, and auth guard
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return <div>{children}</div>;
}
