import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { DashboardPage } from '@/features/professionals'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 30_000,
    },
  },
})

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <DashboardPage />
      </div>
    </QueryClientProvider>
  )
}
