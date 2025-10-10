import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// Add app loaded class after initial render
setTimeout(() => {
  document.body.classList.add('app-loaded');
}, 100);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);