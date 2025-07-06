"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

interface Equipamento {
  id: number;
  nome: string;
  tipo: string;
  fabricante?: string;
  cliente_nome: string;
  empreendimento_nome: string;
}

export default function EquipamentosPage() {
  const [equipamentos, setEquipamentos] = useState<Equipamento[]>([]);

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/equipamentos/")
      .then((res) => res.json())
      .then(setEquipamentos);
  }, []);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-green-800">Equipamentos</h1>
        <div className="flex gap-2">
          <Link href="/" className="bg-gray-300 text-gray-800 px-3 py-1 rounded hover:bg-gray-400">
            🏠 Home
          </Link>
          <Link href="/equipamentos/novo" className="bg-green-700 text-white px-4 py-2 rounded hover:bg-green-800">
            + Novo
          </Link>
        </div>
      </div>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {equipamentos.map((e) => (
          <div key={e.id} className="border p-4 rounded shadow">
            <h2 className="font-semibold">{e.nome} ({e.tipo})</h2>
            <p>Cliente: {e.cliente_nome}</p>
            <p>Empreendimento: {e.empreendimento_nome}</p>
            <p>Fabricante: {e.fabricante || "—"}</p>
            <Link
              href={`/equipamentos/editar/${e.id}`}
              className="text-blue-600 underline mt-2 inline-block"
            >
              ✏️ Editar
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
