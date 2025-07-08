"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

export default function NovoFornecedorPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    nome_fantasia: "",
    razao_social: "",
    cnpj: "",
    telefone: "",
    email: "",
    endereco: "",
    observacoes: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post("https://mandacaru-backend-i2ci.onrender.com/api/fornecedores/", formData);
      router.push("/fornecedores");
    } catch (error: any) {
      if (error.response && error.response.data && error.response.data.cnpj) {
        alert(`Erro: ${error.response.data.cnpj[0]}`);
      } else {
        console.error("Erro ao cadastrar fornecedor:", error);
        alert("Erro ao cadastrar fornecedor. Verifique os dados.");
      }
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-green-800 mb-4">Novo Fornecedor</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          name="nome_fantasia"
          placeholder="Nome Fantasia"
          value={formData.nome_fantasia}
          onChange={handleChange}
          required
          className="w-full p-2 border rounded"
        />
        <input
          name="razao_social"
          placeholder="Razão Social"
          value={formData.razao_social}
          onChange={handleChange}
          className="w-full p-2 border rounded"
        />
        <input
          name="cnpj"
          placeholder="CNPJ"
          value={formData.cnpj}
          onChange={handleChange}
          className="w-full p-2 border rounded"
        />
        <input
          name="telefone"
          placeholder="Telefone"
          value={formData.telefone}
          onChange={handleChange}
          className="w-full p-2 border rounded"
        />
        <input
          name="email"
          type="email"
          placeholder="E-mail"
          value={formData.email}
          onChange={handleChange}
          className="w-full p-2 border rounded"
        />
        <input
          name="endereco"
          placeholder="Endereço"
          value={formData.endereco}
          onChange={handleChange}
          className="w-full p-2 border rounded"
        />
        <textarea
          name="observacoes"
          placeholder="Observações"
          value={formData.observacoes}
          onChange={handleChange}
          className="w-full p-2 border rounded"
        />
        <div className="flex gap-4">
          <button
            type="submit"
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Salvar
          </button>
          <button
            type="button"
            onClick={() => router.push("/fornecedores")}
            className="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
}
