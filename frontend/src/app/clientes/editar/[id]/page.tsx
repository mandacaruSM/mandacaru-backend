// /src/app/clientes/editar/[id]/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

interface Cliente {
  nome_razao: string;
  nome_fantasia: string;
  cnpj: string;
  inscricao_estadual: string;
  telefone: string;
  email: string;
  endereco: string;
  cidade: string;
  estado: string;
  cep: string;
  observacoes: string;
}

export default function EditarClientePage() {
  const { id } = useParams();
  const router = useRouter();
  const [formData, setFormData] = useState<Cliente | null>(null);

  useEffect(() => {
    if (id) {
      fetch(`https://mandacaru-backend-i2ci.onrender.com/api/clientes/${id}/`)
        .then((res) => res.json())
        .then((data) => setFormData(data))
        .catch(() => alert("Erro ao carregar cliente."));
    }
  }, [id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    if (!formData) return;
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData) return;

    await fetch(`https://mandacaru-backend-i2ci.onrender.com/api/clientes/${id}/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    router.push("/clientes");
  };

  if (!formData) return <p className="text-center">Carregando cliente...</p>;

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-green-800 mb-4">Editar Cliente</h1>
      <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
        <input name="nome_razao" value={formData.nome_razao} onChange={handleChange} placeholder="Nome/Razão Social" className="border p-2 rounded" required />
        <input name="nome_fantasia" value={formData.nome_fantasia} onChange={handleChange} placeholder="Nome Fantasia" className="border p-2 rounded" required />
        <input name="cnpj" value={formData.cnpj} onChange={handleChange} placeholder="CNPJ" className="border p-2 rounded" required />
        <input name="inscricao_estadual" value={formData.inscricao_estadual} onChange={handleChange} placeholder="Inscrição Estadual" className="border p-2 rounded" />
        <input name="telefone" value={formData.telefone} onChange={handleChange} placeholder="Telefone" className="border p-2 rounded" />
        <input name="email" value={formData.email} onChange={handleChange} placeholder="E-mail" className="border p-2 rounded" />
        <input name="endereco" value={formData.endereco} onChange={handleChange} placeholder="Endereço" className="border p-2 rounded" />
        <input name="cidade" value={formData.cidade} onChange={handleChange} placeholder="Cidade" className="border p-2 rounded" />
        <input name="estado" value={formData.estado} onChange={handleChange} placeholder="Estado" className="border p-2 rounded" />
        <input name="cep" value={formData.cep} onChange={handleChange} placeholder="CEP" className="border p-2 rounded" />
        <textarea name="observacoes" value={formData.observacoes} onChange={handleChange} placeholder="Observações" className="border p-2 rounded col-span-2" />
        <div className="col-span-2 flex justify-between">
          <button type="button" onClick={() => router.push("/clientes")} className="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500">
            Voltar
          </button>
          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
            Salvar Alterações
          </button>
        </div>
      </form>
    </div>
  );
}
