
"use client"

import { useEffect, useState } from "react";

interface Cliente {
  id: number;
  nome_fantasia: string;
}

interface Empreendimento {
  id: number;
  nome: string;
  cliente: number;
  cliente_nome?: string;
  localizacao: string;
  descricao: string;
  distancia_km: string;
}

export default function EmpreendimentoForm() {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [empreendimentos, setEmpreendimentos] = useState<Empreendimento[]>([]);
  const [formData, setFormData] = useState({
    nome: "",
    cliente: "",
    localizacao: "",
    descricao: "",
    distancia_km: ""
  });

  const fetchClientes = async () => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/clientes/`);
    const data = await res.json();
    setClientes(data);
  };

  const fetchEmpreendimentos = async () => {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/empreendimentos/`);
    const data = await res.json();
    setEmpreendimentos(data);
  };

  useEffect(() => {
    fetchClientes();
    fetchEmpreendimentos();
  }, []);

  const handleChange = (e: any) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/empreendimentos/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });
    if (res.ok) {
      alert("Empreendimento cadastrado com sucesso!");
      setFormData({ nome: "", cliente: "", localizacao: "", descricao: "", distancia_km: "" });
      fetchEmpreendimentos();
    } else {
      alert("Erro ao cadastrar empreendimento.");
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto text-white">
      <form onSubmit={handleSubmit} className="bg-gray-800 p-4 rounded-md space-y-4">
        <h2 className="text-xl font-bold">Novo Empreendimento</h2>

        <input name="nome" placeholder="Nome" value={formData.nome} onChange={handleChange} required className="w-full p-2 bg-gray-700 rounded" />
        <select name="cliente" value={formData.cliente} onChange={handleChange} required className="w-full p-2 bg-gray-700 rounded">
          <option value="">Selecione um cliente</option>
          {clientes.map(c => <option key={c.id} value={c.id}>{c.nome_fantasia}</option>)}
        </select>
        <input name="localizacao" placeholder="Localização (opcional)" value={formData.localizacao} onChange={handleChange} className="w-full p-2 bg-gray-700 rounded" />
        <input name="distancia_km" type="number" step="0.01" placeholder="Distância (km)" value={formData.distancia_km} onChange={handleChange} className="w-full p-2 bg-gray-700 rounded" />
        <textarea name="descricao" placeholder="Descrição" value={formData.descricao} onChange={handleChange} className="w-full p-2 bg-gray-700 rounded" />

        <button type="submit" className="bg-blue-600 hover:bg-blue-700 py-2 px-4 rounded w-full">Salvar</button>
      </form>

      <div className="mt-6">
        <h3 className="text-lg font-semibold">Empreendimentos Cadastrados</h3>
        <ul className="space-y-2 mt-2">
          {empreendimentos.map(e => (
            <li key={e.id} className="bg-gray-700 p-3 rounded">
              <p className="font-bold">{e.nome}</p>
              <p className="text-sm text-gray-300">{e.cliente_nome}</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
