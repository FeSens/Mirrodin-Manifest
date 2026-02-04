import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './App.css';

// Import mana and keyrune fonts
import 'mana-font/css/mana.css';
import 'keyrune/css/keyrune.css';

createRoot(document.getElementById('app')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
