// frontend/src/app/ordens-servico/page.tsx

"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface OrdemServico {
  id: number;
  cliente: number;
  cliente_nome: string;
  equipamento: number;
  equipamento_nome: string;
  data_abertura: string;
  finalizada: boolean;
}

export default function OrdensServicoPage() {
  const [ordens, setOrdens] = useState<OrdemServico[]>([]);
  const [loading, setLoading] = useState(true);
  const [mostrarFinalizadas, setMostrarFinalizadas] = useState(false);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/ordens-servico/`)
      .then(res => res.json())
      .then(data => setOrdens(data))
      .catch(() => alert("Erro ao carregar ordens de serviço."))
      .finally(() => setLoading(false));
  }, []);

  const filtradas = ordens.filter(os => os.finalizada === mostrarFinalizadas);

  if (loading) return <p className="p-6">Carregando ordens…</p>;

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Ordens de Serviço</h1>
        <Link href="/ordens-servico/novo" className="bg-green-600 text-white px-4 py-2 rounded">
          + Nova OS
        </Link>
      </div>
      <div className="flex items-center gap-4">
        <label>
          <input
            type="checkbox"
            checked={mostrarFinalizadas}
            onChange={() => setMostrarFinalizadas(!mostrarFinalizadas)}
          />{' '}
          Mostrar Finalizadas
        </label>
      </div>
      <table className="w-full border-collapse">
        <thead className="bg-gray-200">
          <tr>
            <th className="border p-2">ID</th>
            <th className="border p-2">Cliente</th>
            <th className="border p-2">Equipamento</th>
            <th className="border p-2">Abertura</th>
            <th className="border p-2">Status</th>
            <th className="border p-2">Ações</th>
          </tr>
        </thead>
        <tbody>
          {filtradas.map(os => (
            <tr key={os.id}>
              <td className="border p-2">{os.id}</td>
              <td className="border p-2">{os.cliente_nome}</td>
              <td className="border p-2">{os.equipamento_nome}</td>
              <td className="border p-2">{new Date(os.data_abertura).toLocaleString()}</td>
              <td className="border p-2">{os.finalizada ? 'Finalizada' : 'Aberta'}</td>
              <td className="border p-2">
                <Link href={`/ordens-servico/editar/${os.id}`} className="text-blue-600">
                  Editar
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}