/* File: app/orcamentos/page.tsx */

"use client";
import { useState, useEffect } from "react";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL!; // ex: https://mandacaru-backend-i2ci.onrender.com

interface Orcamento {
  id: number;
  cliente_nome: string;
  equipamento_nome: string;
  valor: number;
  status: string;
}

export default function OrcamentosPage() {
  const [items, setItems] = useState<Orcamento[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/orcamentos/`)
      .then(res => {
        if (!res.ok) throw new Error(`Erro ao buscar orçamentos: ${res.status}`);
        return res.json();
      })
      .then((data: any[]) => {
        const parsed = data.map(o => ({
          id: o.id,
          cliente_nome: o.cliente_obj?.nome_fantasia || "-",
          equipamento_nome: o.equipamento_obj?.nome || "-",
          valor: o.valor,
          status: o.status,
        }));
        setItems(parsed);
      })
      .catch(() => alert("Erro ao carregar orçamentos."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="p-6">Carregando orçamentos…</p>;

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Orçamentos</h1>
        <Link
          href="/orcamentos/novo"
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          + Novo Orçamento
        </Link>
      </div>
      <table className="w-full border text-sm">
        <thead>
          <tr className="bg-gray-100">
            <th className="border p-2">ID</th>
            <th className="border p-2">Cliente</th>
            <th className="border p-2">Equipamento</th>
            <th className="border p-2">Valor</th>
            <th className="border p-2">Status</th>
            <th className="border p-2 text-center">Ações</th>
          </tr>
        </thead>
        <tbody>
          {items.map(o => (
            <tr key={o.id} className="border-b hover:bg-gray-50">
              <td className="border p-2">{o.id}</td>
              <td className="border p-2">{o.cliente_nome}</td>
              <td className="border p-2">{o.equipamento_nome}</td>
              <td className="border p-2">{o.valor.toFixed(2)}</td>
              <td className="border p-2">{o.status}</td>
              <td className="border p-2 text-center">
                <Link
                  href={`/orcamentos/editar/${o.id}`}
                  className="bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700"
                >
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