// src/pages/TicketsList.tsx
import { useEffect, useState } from 'react';
import { getTickets } from '../api/tickets';
import type { Ticket } from '../types/ticket';

export function TicketsList() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getTickets()
      .then((data) => {
        setTickets(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError('Erro ao carregar os tickets. Verifique se o backend está rodando.');
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-6">Carregando tickets...</div>;
  if (error) return <div className="p-6 text-red-500">{error}</div>;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Meus Chamados</h1>
      {tickets.length === 0 ? (
        <p>Nenhum chamado encontrado.</p>
      ) : (
        <div className="space-y-3">
          {tickets.map((ticket) => (
            <div key={ticket.id} className="p-4 border rounded-lg shadow-sm bg-white">
              <div className="flex justify-between items-center">
                <h3 className="font-semibold text-lg">{ticket.title}</h3>
                <span className="px-2 py-1 text-xs rounded bg-gray-100 uppercase font-bold">
                  {ticket.status}
                </span>
              </div>
              <p className="text-gray-600 text-sm mt-1">{ticket.description}</p>
              <div className="mt-3 text-xs text-gray-400 flex gap-4">
                <span>Prioridade: {ticket.priority}</span>
                <span>Categoria: {ticket.category}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}