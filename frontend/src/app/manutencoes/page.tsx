// /src/app/manutencoes/page.tsx
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Manutencao {
  id: number;
  equipamento_nome: string;
  tipo: string;
  data: string;
  horimetro: string;
  tecnico_responsavel: string;
}

export default function ListaManutencoes() {
  const [manutencoes, setManutencoes] = useState<Manutencao[]>([]);

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/manutencoes/")
      .then((res) => res.json())
      .then((data) => setManutencoes(data))
      .catch(() => alert("Erro ao carregar manutenções."));
  }, []);

  const handleDelete = async (id: number) => {
    if (confirm("Tem certeza que deseja excluir esta manutenção?")) {
      const res = await fetch(
        `https://mandacaru-backend-i2ci.onrender.com/api/manutencoes/${id}/`,
        {
          method: "DELETE",
        }
      );
      if (res.ok) {
        setManutencoes(manutencoes.filter((m) => m.id !== id));
      } else {
        alert("Erro ao excluir.");
      }
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-green-800">Histórico de Manutenções</h1>
        <div className="flex gap-2">
          <Link
            href="/"
            className="bg-gray-300 text-gray-800 px-3 py-1 rounded hover:bg-gray-400"
          >
            🏠 Início
          </Link>
          <Link
            href="/manutencoes/novo"
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            + Nova Manutenção
          </Link>
        </div>
      </div>
      <table className="w-full border text-sm">
        <thead>
          <tr className="bg-green-100">
            <th className="border p-2 text-left">Equipamento</th>
            <th className="border p-2 text-left">Tipo</th>
            <th className="border p-2 text-left">Data</th>
            <th className="border p-2 text-left">Horímetro</th>
            <th className="border p-2 text-left">Técnico</th>
            <th className="border p-2">Ações</th>
          </tr>
        </thead>
        <tbody>
          {manutencoes.map((m) => (
            <tr key={m.id} className="border-b hover:bg-green-50">
              <td className="border p-2">{m.equipamento_nome}</td>
              <td className="border p-2 capitalize">{m.tipo}</td>
              <td className="border p-2">{m.data}</td>
              <td className="border p-2">{m.horimetro}</td>
              <td className="border p-2">{m.tecnico_responsavel}</td>
              <td className="border p-2 text-center space-x-2">
                <Link
                  href={`/manutencoes/editar/${m.id}`}
                  className="bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700"
                >
                  Editar
                </Link>
                <button
                  onClick={() => handleDelete(m.id)}
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
