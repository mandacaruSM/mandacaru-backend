"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Empreendimento {
  id: number;
  nome: string;
  cliente_nome: string;
  localizacao: string;
  distancia_km: string;
}

export default function EmpreendimentosPage() {
  const [data, setData] = useState<Empreendimento[]>([]);

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/empreendimentos/")
      .then((res) => res.json())
      .then((data) => setData(data));
  }, []);

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-green-800">Empreendimentos</h1>
        <Link href="/empreendimentos/novo" className="bg-green-700 text-white px-4 py-2 rounded hover:bg-green-800">
          Novo Empreendimento
        </Link>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.map((emp) => (
          <div key={emp.id} className="border p-4 rounded shadow">
            <h2 className="text-lg font-semibold">{emp.nome}</h2>
            <p className="text-sm text-gray-600">Cliente: {emp.cliente_nome}</p>
            <p className="text-sm">Localização: {emp.localizacao}</p>
            <p className="text-sm">Distância: {emp.distancia_km} km</p>
            <Link href={`/empreendimentos/editar/${emp.id}`} className="text-green-700 underline mt-2 inline-block">Editar</Link>
          </div>
        ))}
      </div>
    </div>
  );
}
