"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Cliente {
  id: number;
  nome_fantasia: string;
  cnpj: string;
  inscricao_estadual: string;
  endereco: string;
  cidade: string;
  estado: string;
  telefone: string;
  email: string;
}

export default function ClienteList({ recarregar }: { recarregar: boolean }) {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    const fetchClientes = async () => {
      try {
        const res = await fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/");
        if (!res.ok) throw new Error("Erro ao buscar clientes");
        const data: Cliente[] = await res.json();
        setClientes(data);
      } catch {
        setErro("Não foi possível carregar os clientes.");
      }
    };

    fetchClientes();
  }, [recarregar]);

  const excluirCliente = async (id: number) => {
    const confirmar = confirm("Tem certeza que deseja excluir este cliente?");
    if (!confirmar) return;

    try {
      const res = await fetch(`https://mandacaru-backend-i2ci.onrender.com/api/clientes/${id}/`, {
        method: "DELETE",
      });
      if (!res.ok) throw new Error("Erro ao excluir");
      setClientes((prev) => prev.filter((cliente) => cliente.id !== id));
    } catch {
      alert("Erro ao excluir cliente.");
    }
  };

  if (erro) {
    return <div className="text-red-600 font-semibold">{erro}</div>;
  }

  return (
    <ul className="space-y-2">
      {clientes.map((cliente) => (
        <li key={cliente.id} className="bg-white p-4 rounded shadow hover:shadow-md">
          <div className="flex justify-between items-center">
            <div>
              <div className="text-lg font-semibold text-green-900">{cliente.nome_fantasia}</div>
              <div className="text-sm text-gray-600">{cliente.cidade} - {cliente.estado}</div>
              <div className="text-sm text-gray-600">CNPJ: {cliente.cnpj}</div>
              <div className="text-sm text-gray-600">Tel: {cliente.telefone}</div>
            </div>
            <div className="flex gap-4 items-center">
              <Link
                href={`/clientes/${cliente.id}/editar`}
                className="text-sm text-blue-600 hover:underline"
              >
                Editar
              </Link>
              <button
                onClick={() => excluirCliente(cliente.id)}
                className="text-sm text-red-600 hover:underline"
              >
                Excluir
              </button>
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}
