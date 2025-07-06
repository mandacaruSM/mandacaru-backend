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

export default function EditarEquipamento() {
  const { id } = useParams();
  const router = useRouter();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [empreendimentos, setEmpreendimentos] = useState<Empreendimento[]>([]);
  const [formData, setFormData] = useState<null | {
    nome: string;
    tipo: string;
    fabricante: string;
    modelo: string;
    numero_serie: string;
    cliente: string;
    empreendimento: string;
    observacoes: string;
  }>(null);

  useEffect(() => {
    if (typeof id !== "string") return;

    fetch(`https://mandacaru-backend-i2ci.onrender.com/api/equipamentos/${id}/`)
      .then((res) => res.json())
      .then((data) => {
        setFormData({
          ...data,
          cliente: String(data.cliente),
          empreendimento: String(data.empreendimento),
        });
      });

    fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/")
      .then((res) => res.json())
      .then(setClientes);

    fetch("https://mandacaru-backend-i2ci.onrender.com/api/empreendimentos/")
      .then((res) => res.json())
      .then(setEmpreendimentos);
  }, [id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    if (!formData) return;
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData || typeof id !== "string") return;

    await fetch(`https://mandacaru-backend-i2ci.onrender.com/api/equipamentos/${id}/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    router.push("/equipamentos");
  };

  if (!formData) return <div className="p-4">Carregando...</div>;

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-green-800">Editar Equipamento</h2>
        <Link href="/" className="bg-gray-300 text-gray-800 px-3 py-1 rounded hover:bg-gray-400">
          🏠 Home
        </Link>
      </div>
      <form onSubmit={handleSubmit} className="grid gap-4">
        <input name="nome" value={formData.nome} onChange={handleChange} className="border rounded p-2" placeholder="Nome" />
        <input name="tipo" value={formData.tipo} onChange={handleChange} className="border rounded p-2" placeholder="Tipo" />
        <input name="fabricante" value={formData.fabricante} onChange={handleChange} className="border rounded p-2" placeholder="Fabricante" />
        <input name="modelo" value={formData.modelo} onChange={handleChange} className="border rounded p-2" placeholder="Modelo" />
        <input name="numero_serie" value={formData.numero_serie} onChange={handleChange} className="border rounded p-2" placeholder="Número de Série" />

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

        <textarea
          name="observacoes"
          value={formData.observacoes}
          onChange={handleChange}
          className="border rounded p-2"
          placeholder="Observações"
        />

        <button type="submit" className="bg-blue-700 text-white px-4 py-2 rounded hover:bg-blue-600 w-full md:w-auto">
          Salvar Alterações
        </button>
      </form>
    </div>
  );
}
