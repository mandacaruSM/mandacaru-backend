"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function NovoProdutoPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    nome: "",
    descricao: "",
    quantidade: "",
    unidade: "",
    localizacao: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(
        "https://mandacaru-backend-i2ci.onrender.com/api/almoxarifado/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        }
      );

      if (!response.ok) {
        throw new Error("Erro ao salvar produto");
      }

      router.push("/almoxarifado");
    } catch (error) {
      alert("Erro ao salvar produto");
      console.error(error);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-green-800">Novo Produto</h1>
        <Link
          href="/"
          className="bg-gray-300 text-gray-800 px-3 py-1 rounded hover:bg-gray-400"
        >
          🏠 Início
        </Link>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          name="nome"
          value={formData.nome}
          onChange={handleChange}
          placeholder="Nome"
          className="border p-2 w-full"
          required
        />
        <textarea
          name="descricao"
          value={formData.descricao}
          onChange={handleChange}
          placeholder="Descrição"
          className="border p-2 w-full"
        />
        <input
          type="number"
          name="quantidade"
          value={formData.quantidade}
          onChange={handleChange}
          placeholder="Quantidade"
          className="border p-2 w-full"
          required
        />
        <input
          name="unidade"
          value={formData.unidade}
          onChange={handleChange}
          placeholder="Unidade (ex: un, kg, l)"
          className="border p-2 w-full"
          required
        />
        <input
          name="localizacao"
          value={formData.localizacao}
          onChange={handleChange}
          placeholder="Localização no estoque"
          className="border p-2 w-full"
        />

        <button
          type="submit"
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Salvar
        </button>
      </form>

      <Link
        href="/almoxarifado"
        className="inline-block mt-4 text-green-600 hover:underline"
      >
        Voltar para Almoxarifado
      </Link>
    </div>
  );
}
