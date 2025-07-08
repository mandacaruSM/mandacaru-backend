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

interface Equipamento {
  id: number;
  nome: string;
}

export default function NovoOrcamentoPage() {
  const router = useRouter();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [empreendimentos, setEmpreendimentos] = useState<Empreendimento[]>([]);
  const [equipamentos, setEquipamentos] = useState<Equipamento[]>([]);
  const [formData, setFormData] = useState({
    cliente: "",
    empreendimento: "",
    equipamento: "",
    descricao: "",
    valor: "",
    status: "pendente",
  });

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/")
      .then((res) => res.json())
      .then(setClientes);

    fetch("https://mandacaru-backend-i2ci.onrender.com/api/empreendimentos/")
      .then((res) => res.json())
      .then(setEmpreendimentos);

    fetch("https://mandacaru-backend-i2ci.onrender.com/api/equipamentos/")
      .then((res) => res.json())
      .then(setEquipamentos);
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
        "https://mandacaru-backend-i2ci.onrender.com/api/orcamentos/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData),
        }
      );

      if (!response.ok) {
        throw new Error("Erro ao salvar orçamento");
      }

      router.push("/orcamentos");
    } catch (error) {
      alert("Erro ao salvar orçamento");
      console.error(error);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-green-800 mb-4">Novo Orçamento</h1>
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

        <select
          name="equipamento"
          value={formData.equipamento}
          onChange={handleChange}
          required
          className="border p-2 w-full"
        >
          <option value="">Selecione o Equipamento</option>
          {equipamentos.map((e) => (
            <option key={e.id} value={e.id}>
              {e.nome}
            </option>
          ))}
        </select>

        <textarea
          name="descricao"
          value={formData.descricao}
          onChange={handleChange}
          placeholder="Descrição"
          className="border p-2 w-full"
        />

        <input
          type="number"
          step="0.01"
          name="valor"
          value={formData.valor}
          onChange={handleChange}
          placeholder="Valor"
          className="border p-2 w-full"
        />

        <select
          name="status"
          value={formData.status}
          onChange={handleChange}
          required
          className="border p-2 w-full"
        >
          <option value="pendente">Pendente</option>
          <option value="aprovado">Aprovado</option>
          <option value="rejeitado">Rejeitado</option>
        </select>

        <button
          type="submit"
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Salvar
        </button>
      </form>

      <Link
        href="/orcamentos"
        className="inline-block mt-4 text-green-600 hover:underline"
      >
        Voltar
      </Link>
    </div>
  );
}