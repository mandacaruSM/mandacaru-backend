"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

interface Cliente {
  id: number;
  nome_fantasia: string;
}

export default function EditarEmpreendimento() {
  const { id } = useParams();
  const router = useRouter();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [formData, setFormData] = useState({
    nome: "",
    cliente: "",
    localizacao: "",
    descricao: "",
    distancia_km: "",
  });

  useEffect(() => {
    fetch(`https://mandacaru-backend-i2ci.onrender.com/api/empreendimentos/${id}/`)
      .then((res) => res.json())
      .then((data) => setFormData(data));

    fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/")
      .then((res) => res.json())
      .then((data) => setClientes(data));
  }, [id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await fetch(`https://mandacaru-backend-i2ci.onrender.com/api/empreendimentos/${id}/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });
    router.push("/empreendimentos");
  };

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold text-green-800 mb-4">Editar Empreendimento</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input type="text" name="nome" value={formData.nome} onChange={handleChange} className="w-full border rounded p-2" />
        
        <select name="cliente" value={formData.cliente} onChange={handleChange} className="w-full border rounded p-2">
          <option value="">Selecione um Cliente</option>
          {clientes.map((c) => (
            <option key={c.id} value={c.id}>{c.nome_fantasia}</option>
          ))}
        </select>
        
        <input type="text" name="localizacao" value={formData.localizacao} onChange={handleChange} className="w-full border rounded p-2" />
        
        <textarea name="descricao" value={formData.descricao} onChange={handleChange} className="w-full border rounded p-2" />
        
        <input type="number" name="distancia_km" value={formData.distancia_km} onChange={handleChange} className="w-full border rounded p-2" step="0.01" />
        
        <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">Salvar Alterações</button>
      </form>
    </div>
  );
}
