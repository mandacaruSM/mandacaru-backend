// /src/app/almoxarifado/page.tsx
"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

interface Produto {
  id: number;
  codigo: string;
  descricao: string;
  unidade_medida: string;
  estoque_atual: string;
}

export default function ProdutosPage() {
  const [produtos, setProdutos] = useState<Produto[]>([]);

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/produtos/")
      .then(res => res.json())
      .then(data => setProdutos(data));
  }, []);

  return (
    <div className="p-6">
      <div className="flex justify-between mb-4">
        <h1 className="text-2xl font-bold text-green-800">Almoxarifado</h1>
        <Link href="/" className="bg-gray-200 text-gray-800 px-4 py-2 rounded hover:bg-gray-300">🏠 Início</Link>
      </div>
      <Link href="/almoxarifado/novo" className="bg-green-700 text-white px-4 py-2 rounded hover:bg-green-800 mb-4 inline-block">
        ➕ Novo Produto
      </Link>
      <div className="overflow-x-auto">
        <table className="w-full border mt-4 text-sm">
          <thead>
            <tr className="bg-gray-100">
              <th className="border px-2 py-1">Código</th>
              <th className="border px-2 py-1">Descrição</th>
              <th className="border px-2 py-1">Unidade</th>
              <th className="border px-2 py-1">Estoque</th>
              <th className="border px-2 py-1">Ações</th>
            </tr>
          </thead>
          <tbody>
            {produtos.map(p => (
              <tr key={p.id}>
                <td className="border px-2 py-1">{p.codigo}</td>
                <td className="border px-2 py-1">{p.descricao}</td>
                <td className="border px-2 py-1">{p.unidade_medida}</td>
                <td className="border px-2 py-1">{p.estoque_atual}</td>
                <td className="border px-2 py-1 space-x-2">
                  <Link href={`/almoxarifado/editar/${p.id}`} className="text-blue-600 hover:underline">Editar</Link>
                  <Link href={`/almoxarifado/movimentar/${p.id}`} className="text-green-600 hover:underline">Movimentar</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
