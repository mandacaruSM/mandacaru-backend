"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Cliente {
  id: number;
  razao_social: string;
  nome_fantasia?: string;
  cnpj: string;
  email?: string;
  telefone?: string;
  cidade: string;
  estado: string;
}

interface ClienteListProps {
  recarregar: boolean;
}

export default function ClienteList({ recarregar }: ClienteListProps) {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchClientes = async () => {
      try {
        const res = await fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/");
        if (!res.ok) throw new Error("Erro na requisição");
        const data = await res.json();
        setClientes(data);
      } catch (error) {
        console.error("Erro ao carregar clientes:", error);
        alert("Erro ao carregar clientes.");
      } finally {
        setLoading(false);
      }
    };

    fetchClientes();
  }, [recarregar]);

  if (loading) return <p>Carregando clientes...</p>;

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-xl font-bold">Clientes Cadastrados</h1>
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
            <th className="border px-2 py-1 text-left">Razão Social</th>
            <th className="border px-2 py-1 text-left">Fantasia</th>
            <th className="border px-2 py-1 text-left">CNPJ</th>
            <th className="border px-2 py-1 text-left">Cidade/UF</th>
            <th className="border px-2 py-1 text-left">Ações</th>
          </tr>
        </thead>
        <tbody>
          {clientes.map((cliente) => (
            <tr key={cliente.id}>
              <td className="border px-2 py-1">{cliente.id}</td>
              <td className="border px-2 py-1">{cliente.razao_social}</td>
              <td className="border px-2 py-1">{cliente.nome_fantasia}</td>
              <td className="border px-2 py-1">{cliente.cnpj}</td>
              <td className="border px-2 py-1">{cliente.cidade} / {cliente.estado}</td>
              <td className="border px-2 py-1">
                <Link
                  href={`/clientes/${cliente.id}/editar`}
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
