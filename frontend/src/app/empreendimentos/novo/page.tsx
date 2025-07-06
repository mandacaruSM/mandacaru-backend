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
    cliente: 0, // corrigido: começa como número
    localizacao: "",
    descricao: "",
    distancia_km: "",
  });

  const router = useRouter();

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/")
      .then((res) => res.json())
      .then(setClientes)
      .catch((err) => {
        console.error(err);
        alert("Erro ao carregar clientes.");
      });
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        cliente: Number(formData.cliente),
        distancia_km: parseFloat(formData.distancia_km),
      };

      console.log("Payload enviado:", payload); // opcional para debug

      const res = await fetch("https://mandacaru-backend-i2ci.onrender.com/api/empreendimentos/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("Erro ao salvar empreendimento");

      router.push("/empreendimentos");
    } catch (error) {
      console.error(error);
      alert("Erro ao salvar empreendimento.");
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold text-green-800 mb-4">Novo Empreendimento</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          name="nome"
          placeholder="Nome"
          onChange={handleChange}
          className="w-full border rounded p-2"
          required
        />

        <select
          name="cliente"
          value={formData.cliente}
          onChange={handleChange}
          required
          className="w-full border rounded p-2"
        >
          <option value={0}>Selecione um Cliente</option>
          {clientes.map((c) => (
            <option key={c.id} value={c.id}>
              {c.nome_fantasia}
            </option>
          ))}
        </select>

        <input
          type="text"
          name="localizacao"
          placeholder="Localização"
          onChange={handleChange}
          className="w-full border rounded p-2"
        />
        <textarea
          name="descricao"
          placeholder="Descrição"
          onChange={handleChange}
          className="w-full border rounded p-2"
        />
        <input
          type="number"
          name="distancia_km"
          placeholder="Distância (km)"
          onChange={handleChange}
          className="w-full border rounded p-2"
          step="0.01"
        />

        <div className="flex justify-between">
          <button
            type="button"
            onClick={() => router.push("/empreendimentos")}
            className="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500"
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Salvar
          </button>
        </div>
      </form>
    </div>
  );
}
