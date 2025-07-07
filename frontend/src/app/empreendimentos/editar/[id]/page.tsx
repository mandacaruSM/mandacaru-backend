"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

interface Cliente {
  id: number;
  nome_fantasia: string;
}

export default function EditarEmpreendimento() {
  const { id } = useParams();
  const router = useRouter();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [formData, setFormData] = useState<null | {
    nome: string;
    cliente: string | number;
    endereco: string;
    cidade: string;
    estado: string;
    cep: string;
    localizacao: string;
    descricao: string;
    distancia_km: string;
  }>(null);

  useEffect(() => {
    if (typeof id === "string") {
      // Carrega dados do empreendimento
      fetch(`https://mandacaru-backend-i2ci.onrender.com/api/empreendimentos/${id}/`)
        .then((res) => res.json())
        .then((data) => {
          setFormData({
            ...data,
            cliente: String(data.cliente), // garante compatibilidade com o <select>
            distancia_km: String(data.distancia_km),
          });
        });

      // Carrega lista de clientes
      fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/")
        .then((res) => res.json())
        .then(setClientes);
    }
  }, [id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    if (formData) {
      setFormData({ ...formData, [e.target.name]: e.target.value });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData || typeof id !== "string") return;

    const payload = {
      ...formData,
      cliente: Number(formData.cliente),
      distancia_km: parseFloat(formData.distancia_km),
    };

    const res = await fetch(`https://mandacaru-backend-i2ci.onrender.com/api/empreendimentos/${id}/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (res.ok) {
      router.push("/empreendimentos");
    } else {
      alert("Erro ao salvar alterações.");
    }
  };

  if (!formData) return <div className="p-4">Carregando...</div>;

  return (
    <div className="p-6 max-w-xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-green-800">Editar Empreendimento</h1>
        <Link href="/" className="bg-gray-200 text-gray-800 px-3 py-1 rounded hover:bg-gray-300">
          🏠 Home
        </Link>
      </div>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          name="nome"
          value={formData.nome}
          onChange={handleChange}
          className="w-full border rounded p-2"
          placeholder="Nome do Empreendimento"
          required
        />

        <select
          name="cliente"
          value={formData.cliente}
          onChange={handleChange}
          className="w-full border rounded p-2"
          required
        >
          <option value="">Selecione um Cliente</option>
          {clientes.map((c) => (
            <option key={c.id} value={c.id}>
              {c.nome_fantasia}
            </option>
          ))}
        </select>

        <input
          type="text"
          name="endereco"
          value={formData.endereco}
          onChange={handleChange}
          className="w-full border rounded p-2"
          placeholder="Endereço"
          required
        />

        <input
          type="text"
          name="cidade"
          value={formData.cidade}
          onChange={handleChange}
          className="w-full border rounded p-2"
          placeholder="Cidade"
          required
        />

        <input
          type="text"
          name="estado"
          value={formData.estado}
          onChange={handleChange}
          className="w-full border rounded p-2"
          maxLength={2}
          placeholder="UF (ex: MG)"
          required
        />

        <input
          type="text"
          name="cep"
          value={formData.cep}
          onChange={handleChange}
          className="w-full border rounded p-2"
          placeholder="CEP"
          required
        />

        <input
          type="text"
          name="localizacao"
          value={formData.localizacao}
          onChange={handleChange}
          className="w-full border rounded p-2"
          placeholder="Localização"
        />

        <textarea
          name="descricao"
          value={formData.descricao}
          onChange={handleChange}
          className="w-full border rounded p-2"
          placeholder="Descrição"
        />

        <input
          type="number"
          name="distancia_km"
          value={formData.distancia_km}
          onChange={handleChange}
          className="w-full border rounded p-2"
          placeholder="Distância (KM)"
          step="0.01"
          required
        />

        <button
          type="submit"
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 w-full md:w-auto"
        >
          Salvar Alterações
        </button>
      </form>
    </div>
  );
}
