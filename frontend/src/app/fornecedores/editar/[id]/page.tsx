// /src/app/fornecedores/editar/[id]/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

interface Fornecedor {
  nome_fantasia: string;
  razao_social: string;
  cnpj: string;
  telefone: string;
  email: string;
  endereco: string;
  observacoes: string;
}

export default function EditarFornecedorPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const { id } = params;

  const [formData, setFormData] = useState<Fornecedor>({
    nome_fantasia: "",
    razao_social: "",
    cnpj: "",
    telefone: "",
    email: "",
    endereco: "",
    observacoes: "",
  });

  useEffect(() => {
    axios.get<Fornecedor>(`https://mandacaru-backend-i2ci.onrender.com/api/fornecedores/${id}/`)
      .then((res) => setFormData(res.data))
      .catch((err) => console.error("Erro ao carregar dados do fornecedor:", err));
  }, [id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      await axios.put(`https://mandacaru-backend-i2ci.onrender.com/api/fornecedores/${id}/`, formData);
      router.push("/fornecedores");
    } catch (error) {
      console.error("Erro ao atualizar fornecedor:", error);
      alert("Erro ao salvar. Verifique os dados.");
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-green-800 mb-4">Editar Fornecedor</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input name="nome_fantasia" placeholder="Nome Fantasia" value={formData.nome_fantasia} onChange={handleChange} required className="w-full p-2 border rounded" />
        <input name="razao_social" placeholder="Razão Social" value={formData.razao_social} onChange={handleChange} className="w-full p-2 border rounded" />
        <input name="cnpj" placeholder="CNPJ" value={formData.cnpj} onChange={handleChange} className="w-full p-2 border rounded" />
        <input name="telefone" placeholder="Telefone" value={formData.telefone} onChange={handleChange} className="w-full p-2 border rounded" />
        <input name="email" placeholder="E-mail" value={formData.email} onChange={handleChange} className="w-full p-2 border rounded" />
        <input name="endereco" placeholder="Endereço" value={formData.endereco} onChange={handleChange} className="w-full p-2 border rounded" />
        <textarea name="observacoes" placeholder="Observações" value={formData.observacoes} onChange={handleChange} className="w-full p-2 border rounded" />

        <div className="flex gap-4">
          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">Salvar</button>
          <button type="button" onClick={() => router.push("/fornecedores")} className="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500">Cancelar</button>
        </div>
      </form>
    </div>
  );
}
