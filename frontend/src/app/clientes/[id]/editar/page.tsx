// app/clientes/[id]/editar/page.tsx
"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function EditarCliente() {
  const { id } = useParams();
  const router = useRouter();
  const [formData, setFormData] = useState({
    razao_social: "",
    nome_fantasia: "",
    cnpj: "",
    inscricao_estadual: "",
    telefone: "",
    email: "",
    endereco: "",
    cidade: "",
    estado: "",
    cep: "",
  });

  useEffect(() => {
    fetch(`https://mandacaru-backend-i2ci.onrender.com/api/clientes/${id}/`)
      .then((res) => res.json())
      .then((data) => setFormData(data))
      .catch((err) => console.error("Erro ao buscar cliente:", err));
  }, [id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const response = await fetch(`https://mandacaru-backend-i2ci.onrender.com/api/clientes/${id}/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    if (response.ok) {
      router.push("/clientes");
    } else {
      alert("Erro ao atualizar cliente");
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4 text-blue-800">Editar Cliente #{id}</h2>
      <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <input name="razao_social" placeholder="Razão Social" value={formData.razao_social} onChange={handleChange} required className="border px-3 py-2 rounded" />
        <input name="nome_fantasia" placeholder="Nome Fantasia" value={formData.nome_fantasia} onChange={handleChange} required className="border px-3 py-2 rounded" />
        <input name="cnpj" placeholder="CNPJ" value={formData.cnpj} onChange={handleChange} required className="border px-3 py-2 rounded" />
        <input name="inscricao_estadual" placeholder="Inscrição Estadual" value={formData.inscricao_estadual} onChange={handleChange} className="border px-3 py-2 rounded" />
        <input name="telefone" placeholder="Telefone" value={formData.telefone} onChange={handleChange} required className="border px-3 py-2 rounded" />
        <input name="email" placeholder="Email" type="email" value={formData.email} onChange={handleChange} required className="border px-3 py-2 rounded" />
        <input name="cidade" placeholder="Cidade" value={formData.cidade} onChange={handleChange} required className="border px-3 py-2 rounded" />
        <input name="estado" placeholder="UF" value={formData.estado} maxLength={2} onChange={handleChange} required className="border px-3 py-2 rounded" />
        <input name="cep" placeholder="CEP" value={formData.cep} onChange={handleChange} required className="border px-3 py-2 rounded" />
        <textarea name="endereco" placeholder="Endereço Completo" value={formData.endereco} onChange={handleChange} rows={2} className="border px-3 py-2 rounded col-span-full" />

        <button type="submit" className="bg-blue-700 text-white px-4 py-2 rounded hover:bg-blue-600 col-span-full">
          Atualizar Cliente
        </button>
      </form>
    </div>
  );
}