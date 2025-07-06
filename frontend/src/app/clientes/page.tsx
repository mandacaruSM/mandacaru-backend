"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Cliente {
  id: number;
  nome_fantasia: string;
}

export default function ListaClientes() {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [recarregar, setRecarregar] = useState(false);

  useEffect(() => {
    fetch("http://localhost:8000/api/clientes/")
      .then((res) => res.json())
      .then((data) => setClientes(data))
      .catch((err) => console.error("Erro ao carregar clientes:", err));
  }, [recarregar]);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-green-800">Clientes</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setRecarregar(!recarregar)}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
          >
            Recarregar
          </button>
          <Link
            href="/clientes/novo"
            className="bg-green-700 text-white px-4 py-2 rounded hover:bg-green-600"
          >
            + Novo
          </Link>
        </div>
      </div>
      <ul className="space-y-2">
        {clientes.map((cliente) => (
          <li
            key={cliente.id}
            className="bg-white p-4 rounded shadow hover:shadow-md"
          >
            <div className="flex justify-between">
              <span className="text-lg font-semibold">
                {cliente.nome_fantasia}
              </span>
              <Link
                href={`/clientes/${cliente.id}/editar`}
                className="text-sm text-blue-600 hover:underline"
              >
                Editar
              </Link>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

