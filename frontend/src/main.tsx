import { QueryClient, QueryClientProvider } from "@tanstack/react-query"; // Import React Query
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import App from '@/App';
import '@/index.css';
import { ToastProvider } from "@aminekun90/react-toast";
const queryClient = new QueryClient();
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <App />
      </ToastProvider>
    </QueryClientProvider>
  </StrictMode>
)
