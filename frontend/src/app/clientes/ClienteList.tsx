"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Cliente {
  id: number;
  razao_social: string;
  nome_fantasia?: string;
}

export default function ClienteList({ recarregar }: { recarregar: boolean }) {
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

  if (loading) return <div>Carregando...</div>;
  if (!clientes.length) return <div className="text-gray-600">Nenhum cliente cadastrado.</div>;

  return (
    <ul className="space-y-2">
      {clientes.map((cliente) => (
        <li key={cliente.id} className="bg-white p-4 rounded shadow hover:shadow-md flex justify-between">
          <span className="text-lg font-semibold">{cliente.razao_social}</span>
          <Link
            href={`/clientes/${cliente.id}/editar`}
            className="text-sm text-blue-600 hover:underline"
          >
            Editar
          </Link>
        </li>
      ))}
    </ul>
  );
}
