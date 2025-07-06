"use client";

import { useEffect, useState } from "react";

interface Empreendimento {
  id: number;
  nome: string;
  cliente_nome: string;
  localizacao: string;
  distancia_km: string;
}

export default function EmpreendimentoList() {
  const [empreendimentos, setEmpreendimentos] = useState<Empreendimento[]>([]);

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/empreendimentos/")
      .then((res) => res.json())
      .then((data) => setEmpreendimentos(data));
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-2xl font-bold mb-4 text-green-800">Empreendimentos</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {empreendimentos.map((e) => (
          <div key={e.id} className="border p-4 rounded shadow">
            <h3 className="font-semibold">{e.nome}</h3>
            <p className="text-sm text-gray-700">Cliente: {e.cliente_nome}</p>
            <p className="text-sm">Localização: {e.localizacao}</p>
            <p className="text-sm">Distância: {e.distancia_km} km</p>
          </div>
        ))}
      </div>
    </div>
  );
}
