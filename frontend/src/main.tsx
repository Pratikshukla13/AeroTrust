import { StrictMode } from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { setupStaticInterceptor } from './api/staticInterceptor'

// Install static snapshot interceptor for demo/offline resilience
setupStaticInterceptor()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
