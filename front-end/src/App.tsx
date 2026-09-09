import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import AskPage from './pages/AskPage'
import ChunksPage from './pages/ChunksPage'
import DashboardPage from './pages/DashboardPage'
import IngestPage from './pages/IngestPage'
import UploadPage from './pages/UploadPage'

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/ingest" element={<IngestPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/ask" element={<AskPage />} />
          <Route
            path="/documents/:documentId/chunks"
            element={<ChunksPage />}
          />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
