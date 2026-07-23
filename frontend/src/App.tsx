import { BrowserRouter, Routes, Route } from 'react-router-dom'
import AppLayout from './layout/AppLayout'
import Home from './pages/Home'
import Results from './pages/Results'
import Chat from './pages/Chat'
import About from './pages/About'
import Research from './pages/Research'
import NotFound from './pages/NotFound'

function App() {
  return (
    <BrowserRouter>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/results" element={<Results />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/about" element={<About />} />
          <Route path="/research" element={<Research />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AppLayout>
    </BrowserRouter>
  )
}

export default App