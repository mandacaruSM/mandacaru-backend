// File: src/app/equipamentos/page.tsx

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API = process.env.NEXT_PUBLIC_API_URL!;

interface Equipamento {
  id: number;
  nome: string;
  cliente_nome: string;
  equipamento_nome?: string; // renamed on backend
  modelo: string;
  numero_serie: string;
  descricao: string;
  tipo: string;
  marca: string;
  horimetro: number;
}

export default function ListaEquipamentos() {
  const [equipamentos, setEquipamentos] = useState<Equipamento[]>([]);

  useEffect(() => {
    async function fetchEquipamentos() {
      try {
        const res = await fetch(`${API}/api/equipamentos/`);
        if (!res.ok) throw new Error(`Erro: ${res.status}`);
        const data: Equipamento[] = await res.json();
        setEquipamentos(data);
      } catch {
        alert("Erro ao carregar equipamentos.");
      }
    }
    fetchEquipamentos();
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm("Deseja realmente excluir este equipamento?")) return;
    const res = await fetch(`${API}/api/equipamentos/${id}/`, { method: "DELETE" });
    if (res.ok) {
      setEquipamentos(prev => prev.filter(e => e.id !== id));
    } else {
      alert("Erro ao excluir equipamento.");
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-green-800">Equipamentos</h1>
        <div className="flex gap-2">
          <Link href="/" className="bg-gray-300 text-gray-800 px-3 py-1 rounded hover:bg-gray-400">🏠 Início</Link>
          <Link href="/equipamentos/novo" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">+ Novo Equipamento</Link>
        </div>
      </div>

      <table className="w-full border text-sm">
        <thead>
          <tr className="bg-green-100">
            <th className="border p-2 text-left">Nome</th>
            <th className="border p-2 text-left">Cliente</th>
            <th className="border p-2 text-left">Modelo</th>
            <th className="border p-2 text-left">Nº Série</th>
            <th className="border p-2 text-left">Descrição</th>
            <th className="border p-2 text-left">Tipo</th>
            <th className="border p-2 text-left">Marca</th>
            <th className="border p-2 text-left">Horímetro</th>
            <th className="border p-2 text-center">Ações</th>
          </tr>
        </thead>
        <tbody>
          {equipamentos.map(e => (
            <tr key={e.id} className="border-b hover:bg-green-50">
              <td className="border p-2">{e.nome}</td>
              <td className="border p-2">{e.cliente_nome}</td>
              <td className="border p-2">{e.modelo}</td>
              <td className="border p-2">{e.numero_serie}</td>
              <td className="border p-2">{e.descricao}</td>
              <td className="border p-2">{e.tipo}</td>
              <td className="border p-2">{e.marca}</td>
              <td className="border p-2">{e.horimetro}</td>
              <td className="border p-2 text-center space-x-2">
                <Link href={`/equipamentos/editar/${e.id}`} className="bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700">Editar</Link>
                <button onClick={() => handleDelete(e.id)} className="bg-red-600 text-white px-2 py-1 rounded hover:bg-red-700">Excluir</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
