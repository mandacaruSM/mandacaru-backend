// /src/app/almoxarifado/movimentar/[id]/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

interface Produto {
  id: number;
  codigo: string;
  descricao: string;
  unidade_medida: string;
  estoque_atual: string;
}

export default function MovimentarProdutoPage() {
  const { id } = useParams();
  const router = useRouter();

  const [produto, setProduto] = useState<Produto | null>(null);
  const [formData, setFormData] = useState({
    tipo: "ENTRADA",
    quantidade: "",
    origem: "",
  });

  useEffect(() => {
    fetch(`https://mandacaru-backend-i2ci.onrender.com/api/produtos/${id}/`)
      .then((res) => res.json())
      .then((data) => setProduto(data));
  }, [id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    await fetch(`https://mandacaru-backend-i2ci.onrender.com/api/movimentacoes/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        produto: id,
        ...formData,
      }),
    });

    router.push("/almoxarifado");
  };

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold text-green-800 mb-4">Movimentar Produto</h1>

      {produto && (
        <div className="mb-4 p-4 bg-gray-100 rounded shadow">
          <p><strong>Produto:</strong> {produto.descricao}</p>
          <p><strong>Código:</strong> {produto.codigo}</p>
          <p><strong>Estoque Atual:</strong> {produto.estoque_atual}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <select
          name="tipo"
          value={formData.tipo}
          onChange={handleChange}
          className="w-full border rounded p-2"
        >
          <option value="ENTRADA">Entrada</option>
          <option value="SAIDA">Saída</option>
        </select>

        <input
          type="number"
          name="quantidade"
          step="0.01"
          placeholder="Quantidade"
          value={formData.quantidade}
          onChange={handleChange}
          className="w-full border rounded p-2"
          required
        />

        <input
          type="text"
          name="origem"
          placeholder="Origem ou destino"
          value={formData.origem}
          onChange={handleChange}
          className="w-full border rounded p-2"
        />

        <div className="flex justify-between">
          <button
            type="button"
            onClick={() => router.push("/almoxarifado")}
            className="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500"
          >
            Voltar
          </button>
          <button
            type="submit"
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Confirmar
          </button>
        </div>
      </form>
    </div>
  );
}
