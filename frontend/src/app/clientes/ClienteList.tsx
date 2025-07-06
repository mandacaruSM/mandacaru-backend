"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

interface Cliente {
  id: number;
  razao_social: string;
  nome_fantasia: string;
}

export default function ClienteList({ recarregar = false }: { recarregar?: boolean }) {
  const [clientes, setClientes] = useState<Cliente[]>([]);

  const carregarClientes = async () => {
    try {
      const res = await fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/");
      const data = await res.json();
      setClientes(data);
    } catch (err) {
      console.error("Erro ao carregar clientes:", err);
    }
  };

  const excluirCliente = async (id: number) => {
    const confirmar = confirm("Tem certeza que deseja excluir este cliente?");
    if (!confirmar) return;

    try {
      const res = await fetch(`https://mandacaru-backend-i2ci.onrender.com/api/clientes/${id}/`, {
        method: "DELETE",
      });
      if (res.ok) {
        alert("Cliente excluído com sucesso.");
        carregarClientes();
      } else {
        alert("Erro ao excluir cliente.");
      }
    } catch (err) {
      alert("Erro de conexão ao excluir.");
    }
  };

  useEffect(() => {
    carregarClientes();
  }, [recarregar]);

  return (
    <ul className="space-y-3">
      {clientes.map((cliente) => (
        <li key={cliente.id} className="bg-white p-4 rounded shadow hover:shadow-md">
          <div className="flex justify-between items-center">
            <div>
              <div className="text-lg font-semibold text-green-800">
                {cliente.nome_fantasia || cliente.razao_social}
              </div>
              <div className="text-sm text-gray-500">{cliente.razao_social}</div>
            </div>
            <div className="flex gap-2">
              <Link
                href={`/clientes/${cliente.id}/editar`}
                className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-500"
              >
                Editar
              </Link>
              <button
                onClick={() => excluirCliente(cliente.id)}
                className="text-sm bg-red-600 text-white px-3 py-1 rounded hover:bg-red-500"
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
