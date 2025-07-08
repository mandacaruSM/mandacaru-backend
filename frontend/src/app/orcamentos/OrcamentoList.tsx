"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Orcamento {
  id: number;
  cliente_nome: string;
  empreendimento_nome: string;
  equipamento_nome: string;
  descricao: string;
  valor: string;
  status: string;
  data_criacao: string;
}

interface OrcamentoListProps {
  recarregar: boolean;
}

export default function OrcamentoList({ recarregar }: OrcamentoListProps) {
  const [orcamentos, setOrcamentos] = useState<Orcamento[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOrcamentos = async () => {
      try {
        const res = await fetch("https://mandacaru-backend-i2ci.onrender.com/api/orcamentos/");
        if (!res.ok) throw new Error("Erro na requisição");
        const data = await res.json();
        setOrcamentos(data);
      } catch (error) {
        console.error("Erro ao carregar orçamentos:", error);
        alert("Erro ao carregar orçamentos.");
      } finally {
        setLoading(false);
      }
    };

    fetchOrcamentos();
  }, [recarregar]);

  if (loading) return <p>Carregando orçamentos...</p>;

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-xl font-bold">Orçamentos Cadastrados</h1>
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
            <th className="border px-2 py-1 text-left">Cliente</th>
            <th className="border px-2 py-1 text-left">Empreendimento</th>
            <th className="border px-2 py-1 text-left">Equipamento</th>
            <th className="border px-2 py-1 text-left">Valor</th>
            <th className="border px-2 py-1 text-left">Status</th>
            <th className="border px-2 py-1 text-left">Data</th>
            <th className="border px-2 py-1 text-left">Ações</th>
          </tr>
        </thead>
        <tbody>
          {orcamentos.map((orcamento) => (
            <tr key={orcamento.id}>
              <td className="border px-2 py-1">{orcamento.id}</td>
              <td className="border px-2 py-1">{orcamento.cliente_nome}</td>
              <td className="border px-2 py-1">{orcamento.empreendimento_nome}</td>
              <td className="border px-2 py-1">{orcamento.equipamento_nome}</td>
              <td className="border px-2 py-1">{orcamento.valor}</td>
              <td className="border px-2 py-1">{orcamento.status}</td>
              <td className="border px-2 py-1">{orcamento.data_criacao}</td>
              <td className="border px-2 py-1">
                <Link
                  href={`/orcamentos/editar/${orcamento.id}`}
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