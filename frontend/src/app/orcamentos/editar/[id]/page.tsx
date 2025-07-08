"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

interface Cliente {
  id: number;
  nome_fantasia: string;
}

interface Empreendimento {
  id: number;
  nome: string;
}

interface Equipamento {
  id: number;
  nome: string;
}

export default function EditarOrcamentoPage() {
  const { id } = useParams();
  const router = useRouter();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [empreendimentos, setEmpreendimentos] = useState<Empreendimento[]>([]);
  const [equipamentos, setEquipamentos] = useState<Equipamento[]>([]);
  const [formData, setFormData] = useState<null | {
    cliente: string;
    empreendimento: string;
    equipamento: string;
    descricao: string;
    valor: string;
    status: string;
  }>(null);

  useEffect(() => {
    if (typeof id !== "string") return;

    fetch(`https://mandacaru-backend-i2ci.onrender.com/api/orcamentos/${id}/`)
      .then((res) => res.json())
      .then((data) => {
        setFormData({
          cliente: String(data.cliente || ""),
          empreendimento: String(data.empreendimento || ""),
          equipamento: String(data.equipamento || ""),
          descricao: data.descricao || "",
          valor: String(data.valor || ""),
          status: data.status || "pendente",
        });
      });

    fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/")
      .then((res) => res.json())
      .then(setClientes);

    fetch("https://mandacaru-backend-i2ci.onrender.com/api/empreendimentos/")
      .then((res) => res.json())
      .then(setEmpreendimentos);

    fetch("https://mandacaru-backend-i2ci.onrender.com/api/equipamentos/")
      .then((res) => res.json())
      .then(setEquipamentos);
  }, [id]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    if (!formData) return;
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData || typeof id !== "string") return;

    const response = await fetch(`https://mandacaru-backend-i2ci.onrender.com/api/orcamentos/${id}/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    if (response.ok) {
      router.push("/orcamentos");
    } else {
      alert("Erro ao salvar alterações");
    }
  };

  if (!formData) return <div className="p-4">Carregando...</div>;

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-green-800">Editar Orçamento</h2>
        <Link href="/" className="bg-gray-300 text-gray-800 px-3 py-1 rounded hover:bg-gray-400">
          🏠 Home
        </Link>
      </div>
      <form onSubmit={handleSubmit} className="grid gap-4">
        <select name="cliente" value={formData.cliente} onChange={handleChange} className="border rounded p-2">
          <option value="">Selecione um Cliente</option>
          {clientes.map((c) => (
            <option key={c.id} value={c.id}>{c.nome_fantasia}</option>
          ))}
        </select>

        <select name="empreendimento" value={formData.empreendimento} onChange={handleChange} className="border rounded p-2">
          <option value="">Selecione um Empreendimento</option>
          {empreendimentos.map((e) => (
            <option key={e.id} value={e.id}>{e.nome}</option>
          ))}
        </select>

        <select name="equipamento" value={formData.equipamento} onChange={handleChange} className="border rounded p-2">
          <option value="">Selecione um Equipamento</option>
          {equipamentos.map((e) => (
            <option key={e.id} value={e.id}>{e.nome}</option>
          ))}
        </select>

        <textarea
          name="descricao"
          value={formData.descricao}
          onChange={handleChange}
          className="border rounded p-2"
          placeholder="Descrição"
        />

        <input
          type="number"
          step="0.01"
          name="valor"
          value={formData.valor}
          onChange={handleChange}
          className="border rounded p-2"
          placeholder="Valor"
        />

        <select name="status" value={formData.status} onChange={handleChange} className="border rounded p-2">
          <option value="pendente">Pendente</option>
          <option value="aprovado">Aprovado</option>
          <option value="rejeitado">Rejeitado</option>
        </select>

        <button type="submit" className="bg-blue-700 text-white px-4 py-2 rounded hover:bg-blue-600 w-full md:w-auto">
          Salvar Alterações
        </button>
      </form>
    </div>
  );
}