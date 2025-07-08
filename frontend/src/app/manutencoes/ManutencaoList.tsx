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
  descricao: string;
  proxima_manutencao: string;
}

interface ManutencaoListProps {
  recarregar: boolean;
}

export default function ManutencaoList({ recarregar }: ManutencaoListProps) {
  const [manutencoes, setManutencoes] = useState<Manutencao[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchManutencoes = async () => {
      try {
        const res = await fetch("https://mandacaru-backend-i2ci.onrender.com/api/manutencoes/");
        if (!res.ok) throw new Error("Erro na requisição");
        const data = await res.json();
        setManutencoes(data);
      } catch (error) {
        console.error("Erro ao carregar manutenções:", error);
        alert("Erro ao carregar manutenções.");
      } finally {
        setLoading(false);
      }
    };

    fetchManutencoes();
  }, [recarregar]);

  if (loading) return <p>Carregando manutenções...</p>;

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-xl font-bold">Manutenções Cadastradas</h1>
        <Link
          href="/"
          className="bg-gray-200 text-gray-800 px-3 py-1 rounded hover:bg-gray-300"
        >
          🏠 Home
        </Link>
      </div>

      <table className="min-w-full border border-gray-300 text-sm">
        <thead>
          <tr className="bg-gray-100">
            <th className="border px-2 py-1 text-left">ID</th>
            <th className="border px-2 py-1 text-left">Equipamento</th>
            <th className="border px-2 py-1 text-left">Tipo</th>
            <th className="border px-2 py-1 text-left">Data</th>
            <th className="border px-2 py-1 text-left">Horímetro</th>
            <th className="border px-2 py-1 text-left">Ações</th>
          </tr>
        </thead>
        <tbody>
          {manutencoes.map((manutencao) => (
            <tr key={manutencao.id}>
              <td className="border px-2 py-1">{manutencao.id}</td>
              <td className="border px-2 py-1">{manutencao.equipamento_nome}</td>
              <td className="border px-2 py-1">{manutencao.tipo}</td>
              <td className="border px-2 py-1">{manutencao.data}</td>
              <td className="border px-2 py-1">{manutencao.horimetro}</td>
              <td className="border px-2 py-1">
                <Link
                  href={`/manutencoes/editar/${manutencao.id}`}
                  className="text-blue-600 hover:underline"
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