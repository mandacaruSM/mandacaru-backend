"use client";

import { useState } from "react";
import Link from "next/link";
import OrcamentoList from "./OrcamentoList";

export default function OrcamentosPage() {
  const [recarregar, setRecarregar] = useState(false);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-green-800">Orçamentos</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setRecarregar(!recarregar)}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
          >
            Recarregar
          </button>
          <Link
            href="/orcamentos/novo"
            className="bg-green-700 text-white px-4 py-2 rounded hover:bg-green-800"
          >
            + Novo Orçamento
          </Link>
        </div>
      </div>
      <OrcamentoList recarregar={recarregar} />
    </div>
  );
}
