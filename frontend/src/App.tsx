import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navigation from './components/Navigation'
import DashboardPageClean from './pages/DashboardPageClean'
import EvaluationPageDirect from './pages/EvaluationPageDirect'
import ResultsPage from './pages/ResultsPage'
import ExportPage from './pages/ExportPage'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <header className="bg-white shadow">
            <div className="max-w-7xl mx-auto py-6 px-4">
              <h1 className="text-3xl font-bold text-gray-900">
                Text-to-SQL Evaluation System
              </h1>
            </div>
          </header>
          <Navigation />
          <main className="max-w-7xl mx-auto py-6 px-4">
            <Routes>
              <Route path="/" element={<DashboardPageClean />} />
              <Route path="/evaluation" element={<EvaluationPageDirect />} />
              <Route path="/evaluation/:queryId" element={<EvaluationPageDirect />} />
              <Route path="/results" element={<ResultsPage />} />
              <Route path="/export" element={<ExportPage />} />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App
