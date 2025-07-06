"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface Cliente {
  id: number;
  nome_fantasia: string;
}

export default function NovoEmpreendimento() {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [formData, setFormData] = useState({
    nome: "",
    cliente: "",
    localizacao: "",
    descricao: "",
    distancia_km: "",
  });
  const router = useRouter();

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/")
      .then((res) => res.json())
      .then((data) => setClientes(data));
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await fetch("https://mandacaru-backend-i2ci.onrender.com/api/empreendimentos/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });
    router.push("/empreendimentos");
  };

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold text-green-800 mb-4">Novo Empreendimento</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input type="text" name="nome" placeholder="Nome" onChange={handleChange} className="w-full border rounded p-2" required />
        
        <select name="cliente" onChange={handleChange} required className="w-full border rounded p-2">
          <option value="">Selecione um Cliente</option>
          {clientes.map((c) => (
            <option key={c.id} value={c.id}>{c.nome_fantasia}</option>
          ))}
        </select>
        
        <input type="text" name="localizacao" placeholder="Localização" onChange={handleChange} className="w-full border rounded p-2" />
        
        <textarea name="descricao" placeholder="Descrição" onChange={handleChange} className="w-full border rounded p-2" />
        
        <input type="number" name="distancia_km" placeholder="Distância (km)" onChange={handleChange} className="w-full border rounded p-2" step="0.01" />
        
        <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">Salvar</button>
      </form>
    </div>
  );
}
