"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface Manutencao {
  id: number;
  equipamento_nome: string;
  tipo: string;
  data: string;
  horimetro: number;
  tecnico_responsavel: string;
}

export default function ManutencoesPage() {
  const [manutencoes, setManutencoes] = useState<Manutencao[]>([]);
  const router = useRouter();

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/manutencoes/")
      .then((res) => res.json())
      .then((data) => setManutencoes(data))
      .catch((err) => {
        console.error("Erro ao buscar manutenções:", err);
      });
  }, []);

  const handleExcluir = async (id: number) => {
    if (!confirm("Tem certeza que deseja excluir esta manutenção?")) return;

    const res = await fetch(`https://mandacaru-backend-i2ci.onrender.com/api/manutencoes/${id}/`, {
      method: "DELETE",
    });

    if (res.ok) {
      setManutencoes((prev) => prev.filter((m) => m.id !== id));
    } else {
      alert("Erro ao excluir manutenção.");
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-green-800">Manutenções</h1>
        <div className="flex gap-2">
          <Link
            href="/manutencoes/nova"
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Nova Manutenção
          </Link>
          <Link
            href="/"
            className="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500"
          >
            🏠 Início
          </Link>
        </div>
      </div>

      {manutencoes.length === 0 ? (
        <p className="text-gray-600">Nenhuma manutenção cadastrada.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full table-auto border border-gray-300">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-2 border">Equipamento</th>
                <th className="p-2 border">Tipo</th>
                <th className="p-2 border">Data</th>
                <th className="p-2 border">Horímetro</th>
                <th className="p-2 border">Técnico</th>
                <th className="p-2 border">Ações</th>
              </tr>
            </thead>
            <tbody>
              {manutencoes.map((m) => (
                <tr key={m.id} className="text-center">
                  <td className="p-2 border">{m.equipamento_nome}</td>
                  <td className="p-2 border">{m.tipo}</td>
                  <td className="p-2 border">{m.data}</td>
                  <td className="p-2 border">{m.horimetro}</td>
                  <td className="p-2 border">{m.tecnico_responsavel}</td>
                  <td className="p-2 border flex justify-center gap-2">
                    <button
                      onClick={() => router.push(`/manutencoes/editar/${m.id}`)}
                      className="bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600"
                    >
                      Editar
                    </button>
                    <button
                      onClick={() => handleExcluir(m.id)}
                      className="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600"
                    >
                      Excluir
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
