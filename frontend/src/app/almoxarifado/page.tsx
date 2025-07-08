"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import axios from "axios";

interface Produto {
  id: number;
  codigo: string;
  descricao: string;
  unidade_medida: string;
  estoque_atual: string;
}

export default function AlmoxarifadoPage() {
  const [produtos, setProdutos] = useState<Produto[]>([]);

  useEffect(() => {
    axios
      .get<Produto[]>("https://mandacaru-backend-i2ci.onrender.com/api/produtos/")
      .then((res) => setProdutos(res.data))
      .catch((err) => console.error("Erro ao carregar produtos:", err));
  }, []);

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-green-800">Almoxarifado</h1>
        <div className="flex gap-2">
          <Link
            href="/almoxarifado/novo"
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Novo Produto
          </Link>
        </div>
      </div>

      <table className="w-full bg-white border shadow rounded text-sm">
        <thead className="bg-gray-100">
          <tr>
            <th className="p-2 text-left">Código</th>
            <th className="p-2 text-left">Descrição</th>
            <th className="p-2 text-left">Unidade</th>
            <th className="p-2 text-left">Estoque Atual</th>
            <th className="p-2 text-left">Ações</th>
          </tr>
        </thead>
        <tbody>
          {produtos.length === 0 ? (
            <tr>
              <td colSpan={5} className="p-4 text-center">
                Nenhum produto encontrado.
              </td>
            </tr>
          ) : (
            produtos.map((produto) => (
              <tr key={produto.id} className="border-t">
                <td className="p-2">{produto.codigo}</td>
                <td className="p-2">{produto.descricao}</td>
                <td className="p-2">{produto.unidade_medida}</td>
                <td className="p-2">{produto.estoque_atual}</td>
                <td className="p-2">
                  <Link
                    href={`/almoxarifado/editar/${produto.id}`}
                    className="text-blue-600 hover:underline mr-2"
                  >
                    Editar
                  </Link>
                  <Link
                    href={`/almoxarifado/movimentar/${produto.id}`}
                    className="text-green-600 hover:underline"
                  >
                    Movimentar
                  </Link>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
