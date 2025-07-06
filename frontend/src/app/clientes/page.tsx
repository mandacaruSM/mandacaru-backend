"use client";

import { useState } from "react";
import Link from "next/link";
import ClienteList from "./ClienteList";

export default function ClientesPage() {
  const [recarregar, setRecarregar] = useState(false);

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
            className="bg-green-700 text-white px-4 py-2 rounded hover:bg-green-800"
          >
            + Novo Cliente
          </Link>
        </div>
      </div>
      <ClienteList recarregar={recarregar} />
    </div>
  );
}
