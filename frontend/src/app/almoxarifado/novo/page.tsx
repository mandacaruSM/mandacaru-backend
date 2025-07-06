// /src/app/almoxarifado/novo/page.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function NovoProdutoPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    codigo: "",
    descricao: "",
    unidade_medida: "",
    estoque_atual: "0.00",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    await fetch("https://mandacaru-backend-i2ci.onrender.com/api/produtos/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    router.push("/almoxarifado");
  };

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold text-green-800 mb-4">Novo Produto</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          name="codigo"
          placeholder="Código"
          value={formData.codigo}
          onChange={handleChange}
          className="w-full border rounded p-2"
          required
        />
        <input
          type="text"
          name="descricao"
          placeholder="Descrição"
          value={formData.descricao}
          onChange={handleChange}
          className="w-full border rounded p-2"
          required
        />
        <input
          type="text"
          name="unidade_medida"
          placeholder="Unidade de Medida (ex: un, kg)"
          value={formData.unidade_medida}
          onChange={handleChange}
          className="w-full border rounded p-2"
          required
        />
        <input
          type="number"
          step="0.01"
          name="estoque_atual"
          placeholder="Estoque Inicial"
          value={formData.estoque_atual}
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
            Salvar Produto
          </button>
        </div>
      </form>
    </div>
  );
}
