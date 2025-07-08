"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface Cliente {
  id: number;
  nome_fantasia: string;
}

interface Empreendimento {
  id: number;
  nome: string;
}

export default function NovoEquipamentoPage() {
  const router = useRouter();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [empreendimentos, setEmpreendimentos] = useState<Empreendimento[]>([]);
  const [formData, setFormData] = useState({
    cliente: "",
    empreendimento: "",
    nome: "",
    descricao: "",
    tipo: "",
    marca: "",
    modelo: "",
    n_serie: "",
    horimetro: "",
  });

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/")
      .then((res) => res.json())
      .then(setClientes);

    fetch("https://mandacaru-backend-i2ci.onrender.com/api/empreendimentos/")
      .then((res) => res.json())
      .then(setEmpreendimentos);
  }, []);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(
        "https://mandacaru-backend-i2ci.onrender.com/api/equipamentos/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData),
        }
      );

      if (!response.ok) {
        throw new Error("Erro ao salvar equipamento");
      }

      router.push("/equipamentos");
    } catch (error) {
      alert("Erro ao salvar equipamento");
      console.error(error);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-green-800 mb-4">Novo Equipamento</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <select
          name="cliente"
          value={formData.cliente}
          onChange={handleChange}
          required
          className="border p-2 w-full"
        >
          <option value="">Selecione o Cliente</option>
          {clientes.map((c) => (
            <option key={c.id} value={c.id}>
              {c.nome_fantasia}
            </option>
          ))}
        </select>

        <select
          name="empreendimento"
          value={formData.empreendimento}
          onChange={handleChange}
          required
          className="border p-2 w-full"
        >
          <option value="">Selecione o Empreendimento</option>
          {empreendimentos.map((e) => (
            <option key={e.id} value={e.id}>
              {e.nome}
            </option>
          ))}
        </select>

        <input
          name="nome"
          value={formData.nome}
          onChange={handleChange}
          placeholder="Nome do equipamento"
          required
          className="border p-2 w-full"
        />

        <textarea
          name="descricao"
          value={formData.descricao}
          onChange={handleChange}
          placeholder="Descrição"
          className="border p-2 w-full"
        />

        <input
          name="tipo"
          value={formData.tipo}
          onChange={handleChange}
          placeholder="Tipo"
          className="border p-2 w-full"
        />

        <input
          name="marca"
          value={formData.marca}
          onChange={handleChange}
          placeholder="Marca"
          className="border p-2 w-full"
        />

        <input
          name="modelo"
          value={formData.modelo}
          onChange={handleChange}
          placeholder="Modelo"
          className="border p-2 w-full"
        />

        <input
          name="n_serie"
          value={formData.n_serie}
          onChange={handleChange}
          placeholder="Número de Série"
          className="border p-2 w-full"
        />

        <input
          type="number"
          step="0.01"
          name="horimetro"
          value={formData.horimetro}
          onChange={handleChange}
          placeholder="Horímetro"
          className="border p-2 w-full"
        />

        <button
          type="submit"
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Salvar
        </button>
      </form>

      <Link
        href="/equipamentos"
        className="inline-block mt-4 text-green-600 hover:underline"
      >
        Voltar
      </Link>
    </div>
  );
}
