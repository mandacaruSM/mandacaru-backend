"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL!; // ex: "https://mandacaru-backend-i2ci.onrender.com"

interface Empreendimento {
  id: number;
  nome: string;
  cliente: number;
  endereco: string;
  cidade: string;
  // ... demais campos, se quiser
}

export default function EmpreendimentosPage() {
  const [items, setItems] = useState<Empreendimento[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/empreendimentos/`)
      .then(res => {
        if (!res.ok) throw new Error(`Status ${res.status}`);
        return res.json();
      })
      .then(setItems)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="p-6">Carregando empreendimentos…</p>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Empreendimentos</h1>
        <Link
          href="/empreendimentos/novo"
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Novo
        </Link>
      </div>
      <table className="min-w-full border">
        <thead>
          <tr className="bg-gray-100">
            <th className="px-4 py-2 border">ID</th>
            <th className="px-4 py-2 border">Nome</th>
            <th className="px-4 py-2 border">Cliente</th>
            <th className="px-4 py-2 border">Cidade</th>
            <th className="px-4 py-2 border">Endereço</th>
            {/* adicione colunas conforme desejar */}
          </tr>
        </thead>
        <tbody>
          {items.map((e) => (
            <tr key={e.id}>
              <td className="px-4 py-2 border">{e.id}</td>
              <td className="px-4 py-2 border">{e.nome}</td>
              <td className="px-4 py-2 border">{e.cliente}</td>
              <td className="px-4 py-2 border">{e.cidade}</td>
              <td className="px-4 py-2 border">{e.endereco}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
