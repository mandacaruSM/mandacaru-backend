// /src/app/empreendimentos/page.tsx
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Empreendimento {
  id: number;
  nome: string;
  cliente_nome: string;
  cidade: string;
  estado: string;
  distancia_km: number;
}

export default function ListaEmpreendimentosPage() {
  const [empreendimentos, setEmpreendimentos] = useState<Empreendimento[]>([]);

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/empreendimentos/")
      .then((res) => res.json())
      .then(setEmpreendimentos)
      .catch(() => alert("Erro ao carregar empreendimentos"));
  }, []);

  const handleDelete = async (id: number) => {
    if (confirm("Tem certeza que deseja excluir este empreendimento?")) {
      const res = await fetch(
        `https://mandacaru-backend-i2ci.onrender.com/api/empreendimentos/${id}/`,
        { method: "DELETE" }
      );
      if (res.ok) {
        setEmpreendimentos(empreendimentos.filter((e) => e.id !== id));
      } else {
        alert("Erro ao excluir empreendimento.");
      }
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-green-800">Empreendimentos</h1>
        <div className="flex gap-2">
          <Link
            href="/"
            className="bg-gray-300 text-gray-800 px-3 py-1 rounded hover:bg-gray-400"
          >
            🏠 Início
          </Link>
          <Link
            href="/empreendimentos/novo"
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            + Novo Empreendimento
          </Link>
        </div>
      </div>

      <table className="w-full border text-sm">
        <thead>
          <tr className="bg-green-100">
            <th className="border p-2 text-left">Nome</th>
            <th className="border p-2 text-left">Cliente</th>
            <th className="border p-2 text-left">Cidade</th>
            <th className="border p-2 text-left">Estado</th>
            <th className="border p-2 text-left">Distância (km)</th>
            <th className="border p-2">Ações</th>
          </tr>
        </thead>
        <tbody>
          {empreendimentos.map((e) => (
            <tr key={e.id} className="border-b hover:bg-green-50">
              <td className="border p-2">{e.nome}</td>
              <td className="border p-2">{e.cliente_nome}</td>
              <td className="border p-2">{e.cidade}</td>
              <td className="border p-2">{e.estado}</td>
              <td className="border p-2">{e.distancia_km} km</td>
              <td className="border p-2 text-center space-x-2">
                <Link
                  href={`/empreendimentos/editar/${e.id}`}
                  className="bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700"
                >
                  Editar
                </Link>
                <button
                  onClick={() => handleDelete(e.id)}
                  className="bg-red-600 text-white px-2 py-1 rounded hover:bg-red-700"
                >
                  Excluir
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
