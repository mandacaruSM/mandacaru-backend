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
    marca: string;
    modelo: string;
    numero_serie: string;
    horimetro_atual: string;
    cliente: string;
    empreendimento: string;
    descricao: string;
  }>(null);

  useEffect(() => {
    if (typeof id !== "string") return;

    fetch(`https://mandacaru-backend-i2ci.onrender.com/api/equipamentos/${id}/`)
      .then((res) => res.json())
      .then((data) => {
        setFormData({
          nome: data.nome || "",
          tipo: data.tipo || "",
          marca: data.marca || "",
          modelo: data.modelo || "",
          numero_serie: data.numero_serie || "",
          horimetro_atual: String(data.horimetro_atual || ""),
          cliente: String(data.cliente || ""),
          empreendimento: String(data.empreendimento || ""),
          descricao: data.descricao || "",
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

    const response = await fetch(`https://mandacaru-backend-i2ci.onrender.com/api/equipamentos/${id}/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    if (response.ok) {
      router.push("/equipamentos");
    } else {
      alert("Erro ao salvar alterações");
    }
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
        <input name="marca" value={formData.marca} onChange={handleChange} className="border rounded p-2" placeholder="Marca" />
        <input name="modelo" value={formData.modelo} onChange={handleChange} className="border rounded p-2" placeholder="Modelo" />
        <input name="numero_serie" value={formData.numero_serie} onChange={handleChange} className="border rounded p-2" placeholder="Número de Série" />
        <input name="horimetro_atual" value={formData.horimetro_atual} onChange={handleChange} className="border rounded p-2" placeholder="Horímetro Atual" />

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
          name="descricao"
          value={formData.descricao}
          onChange={handleChange}
          className="border rounded p-2"
          placeholder="Descrição"
        />

        <button type="submit" className="bg-blue-700 text-white px-4 py-2 rounded hover:bg-blue-600 w-full md:w-auto">
          Salvar Alterações
        </button>
      </form>
    </div>
  );
}
