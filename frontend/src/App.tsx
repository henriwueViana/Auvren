// src/App.tsx
import { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { TicketsList } from './pages/TicketsList';

function MainContent() {
  const { token, logout } = useAuth();
  const [isRegistering, setIsRegistering] = useState(false);

  if (!token) {
    return isRegistering ? (
      <Register onSwitchToLogin={() => setIsRegistering(false)} />
    ) : (
      <Login onSwitchToRegister={() => setIsRegistering(true)} />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b px-6 py-3 flex justify-between items-center shadow-sm">
        <span className="font-semibold text-gray-700">Painel de Chamados</span>
        <button
          onClick={logout}
          className="text-sm px-3 py-1 bg-red-50 text-red-600 rounded hover:bg-red-100 transition"
        >
          Sair
        </button>
      </div>
      <TicketsList />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainContent />
    </AuthProvider>
  );
}