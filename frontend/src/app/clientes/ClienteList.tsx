"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Cliente {
  id: number;
  razao_social: string;
  nome_fantasia?: string;
  cnpj: string;
}

export default function ClienteList({ recarregar }: { recarregar: boolean }) {
  const [clientes, setClientes] = useState<Cliente[]>([]);

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/")
      .then((res) => res.json())
      .then((data) => setClientes(data))
      .catch(() => {
        alert("Erro ao carregar clientes");
      });
  }, [recarregar]);

  const excluirCliente = async (id: number) => {
    if (confirm("Tem certeza que deseja excluir?")) {
      try {
        const res = await fetch(`https://mandacaru-backend-i2ci.onrender.com/api/clientes/${id}/`, {
          method: "DELETE",
        });
        if (res.ok) {
          setClientes(clientes.filter((c) => c.id !== id));
        }
      } catch {
        alert("Erro ao excluir cliente.");
      }
    }
  };

  return (
    <ul className="space-y-2">
      {clientes.map((cliente) => (
        <li key={cliente.id} className="bg-white p-4 rounded shadow hover:shadow-md">
          <div className="flex justify-between">
            <div>
              <div className="text-lg font-semibold">{cliente.razao_social}</div>
              <div className="text-sm text-gray-500">{cliente.nome_fantasia}</div>
              <div className="text-sm text-gray-400">{cliente.cnpj}</div>
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
