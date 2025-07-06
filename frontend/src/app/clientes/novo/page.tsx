"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function NovoCliente() {
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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const response = await fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    if (response.ok) {
      router.push("/clientes");
    } else {
      alert("Erro ao cadastrar cliente");
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4 text-green-800">Novo Cliente</h2>
      <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <input name="razao_social" placeholder="Razão Social" onChange={handleChange} required className="border px-3 py-2 rounded" />
        <input name="nome_fantasia" placeholder="Nome Fantasia" onChange={handleChange} required className="border px-3 py-2 rounded" />
        <input name="cnpj" placeholder="CNPJ" onChange={handleChange} required className="border px-3 py-2 rounded" />
        <input name="inscricao_estadual" placeholder="Inscrição Estadual" onChange={handleChange} className="border px-3 py-2 rounded" />
        <input name="telefone" placeholder="Telefone" onChange={handleChange} required className="border px-3 py-2 rounded" />
        <input name="email" placeholder="Email" type="email" onChange={handleChange} required className="border px-3 py-2 rounded" />
        <input name="cidade" placeholder="Cidade" onChange={handleChange} required className="border px-3 py-2 rounded" />
        <input name="estado" placeholder="UF" onChange={handleChange} maxLength={2} required className="border px-3 py-2 rounded" />
        <input name="cep" placeholder="CEP" onChange={handleChange} required className="border px-3 py-2 rounded" />
        <textarea name="endereco" placeholder="Endereço Completo" onChange={handleChange} rows={2} className="border px-3 py-2 rounded col-span-full" />

        <button type="submit" className="bg-green-700 text-white px-4 py-2 rounded hover:bg-green-600 col-span-full">
          Salvar Cliente
        </button>
      </form>
    </div>
  );
}
