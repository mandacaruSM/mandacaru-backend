// /src/app/almoxarifado/page.tsx
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

interface Produto {
  id: number;
  codigo: string;
  descricao: string;
  unidade_medida: string;
  estoque_atual: string;
}

export default function ListaProdutosPage() {
  const [produtos, setProdutos] = useState<Produto[]>([]);

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/produtos/")
      .then((res) => res.json())
      .then(setProdutos)
      .catch(() => alert("Erro ao carregar produtos"));
  }, []);

  const handleDelete = async (id: number) => {
    if (confirm("Tem certeza que deseja excluir este produto?")) {
      const res = await fetch(
        `https://mandacaru-backend-i2ci.onrender.com/api/produtos/${id}/`,
        {
          method: "DELETE",
        }
      );
      if (res.ok) {
        setProdutos(produtos.filter((p) => p.id !== id));
      } else {
        alert("Erro ao excluir produto. Verifique se ele está vinculado a movimentações.");
      }
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-green-800">Almoxarifado</h1>
        <div className="flex gap-2">
          <Link
            href="/"
            className="bg-gray-300 text-gray-800 px-3 py-1 rounded hover:bg-gray-400"
          >
            🏠 Início
          </Link>
          <Link
            href="/almoxarifado/novo"
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            + Novo Produto
          </Link>
        </div>
      </div>

      <table className="w-full border text-sm">
        <thead>
          <tr className="bg-green-100">
            <th className="border p-2 text-left">Código</th>
            <th className="border p-2 text-left">Descrição</th>
            <th className="border p-2 text-left">Unidade</th>
            <th className="border p-2 text-left">Estoque Atual</th>
            <th className="border p-2">Ações</th>
          </tr>
        </thead>
        <tbody>
          {produtos.map((p) => (
            <tr key={p.id} className="border-b hover:bg-green-50">
              <td className="border p-2">{p.codigo}</td>
              <td className="border p-2">{p.descricao}</td>
              <td className="border p-2">{p.unidade_medida}</td>
              <td className="border p-2">{p.estoque_atual}</td>
              <td className="border p-2 text-center space-x-2">
                <Link
                  href={`/almoxarifado/editar/${p.id}`}
                  className="bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700"
                >
                  Editar
                </Link>
                <Link
                  href={`/almoxarifado/movimentar/${p.id}`}
                  className="bg-yellow-600 text-white px-2 py-1 rounded hover:bg-yellow-700"
                >
                  Movimentar
                </Link>
                <button
                  onClick={() => handleDelete(p.id)}
                  className="bg-red-600 text-white px-2 py-1 rounded hover:bg-red-700"
                >
                  Excluir
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
