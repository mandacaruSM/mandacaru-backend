// /src/app/equipamentos/novo/page.tsx
"use client";

import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";

interface Cliente {
  id: number;
  nome_fantasia: string;
}

interface Empreendimento {
  id: number;
  nome: string;
  cliente: number;
}

export default function NovoEquipamentoPage() {
  const router = useRouter();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [empreendimentos, setEmpreendimentos] = useState<Empreendimento[]>([]);
  const [formData, setFormData] = useState({
    nome: "",
    cliente: "",
    empreendimento: "",
    modelo: "",
    numero_serie: "",
  });

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/")
      .then((res) => res.json())
      .then((data: Cliente[]) => setClientes(data));
  }, []);

  useEffect(() => {
    if (formData.cliente) {
      fetch("https://mandacaru-backend-i2ci.onrender.com/api/empreendimentos/")
        .then((res) => res.json())
        .then((data: Empreendimento[]) => {
          const filtrados = data.filter((e) => e.cliente === parseInt(formData.cliente));
          setEmpreendimentos(filtrados);
        });
    } else {
      setEmpreendimentos([]);
    }
  }, [formData.cliente]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await fetch("https://mandacaru-backend-i2ci.onrender.com/api/equipamentos/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });
    router.push("/equipamentos");
  };

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold text-green-800 mb-4">Novo Equipamento</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          name="nome"
          placeholder="Nome do equipamento"
          value={formData.nome}
          onChange={handleChange}
          className="w-full border rounded p-2"
          required
        />

        <select
          name="cliente"
          value={formData.cliente}
          onChange={handleChange}
          className="w-full border rounded p-2"
          required
        >
          <option value="">Selecione o cliente</option>
          {clientes.map((cliente) => (
            <option key={cliente.id} value={cliente.id}>
              {cliente.nome_fantasia}
            </option>
          ))}
        </select>

        <select
          name="empreendimento"
          value={formData.empreendimento}
          onChange={handleChange}
          className="w-full border rounded p-2"
          required
        >
          <option value="">Selecione o empreendimento</option>
          {empreendimentos.map((emp) => (
            <option key={emp.id} value={emp.id}>
              {emp.nome}
            </option>
          ))}
        </select>

        <input
          type="text"
          name="modelo"
          placeholder="Modelo"
          value={formData.modelo}
          onChange={handleChange}
          className="w-full border rounded p-2"
        />

        <input
          type="text"
          name="numero_serie"
          placeholder="Número de série"
          value={formData.numero_serie}
          onChange={handleChange}
          className="w-full border rounded p-2"
        />

        <div className="flex justify-between">
          <button
            type="button"
            onClick={() => router.push("/equipamentos")}
            className="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500"
          >
            Voltar
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
