/* File: app/equipamentos/novo/page.tsx */

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface Cliente {
  id: number;
  nome_fantasia: string;
}

interface Empreendimento {
  id: number;
  nome: string;
}

interface EquipamentoFormData {
  nome: string;
  marca: string;
  modelo: string;
  numero_serie: string;
  horimetro: string;
  cliente: string;
  empreendimento: string;
}

export default function NovoEquipamentoPage() {
  const router = useRouter();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [empreendimentos, setEmpreendimentos] = useState<Empreendimento[]>([]);
  const [formData, setFormData] = useState<EquipamentoFormData>({
    nome: "",
    marca: "",
    modelo: "",
    numero_serie: "",
    horimetro: "",
    cliente: "",
    empreendimento: "",
  });
  const [loadingEmp, setLoadingEmp] = useState(false);

  useEffect(() => {
    fetch("/api/clientes")
      .then(res => res.json())
      .then(setClientes)
      .catch(console.error);
  }, []);

  useEffect(() => {
    if (!formData.cliente) {
      setEmpreendimentos([]);
      setFormData(d => ({ ...d, empreendimento: "" }));
      return;
    }
    setLoadingEmp(true);
    fetch(`/api/empreendimentos/?cliente=${formData.cliente}`)
      .then(res => res.json())
      .then(data => {
        setEmpreendimentos(data);
        setFormData(d => ({ ...d, empreendimento: "" }));
      })
      .catch(console.error)
      .finally(() => setLoadingEmp(false));
  }, [formData.cliente]);

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData(old => ({ ...old, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        nome: formData.nome,
        marca: formData.marca,
        modelo: formData.modelo,
        numero_serie: formData.numero_serie,
        horimetro: parseFloat(formData.horimetro),
        cliente: Number(formData.cliente),
        empreendimento: Number(formData.empreendimento),
      };
      const res = await fetch("/api/equipamentos/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`Erro ${res.status}`);
      alert("Equipamento cadastrado com sucesso!");
      router.push("/equipamentos");
    } catch (err) {
      console.error(err);
      alert("Falha ao cadastrar equipamento.");
    }
  };

  return (
    <div className="p-6 max-w-lg mx-auto">
      <h1 className="text-2xl font-bold mb-4">Novo Equipamento</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-1">Cliente</label>
          <select
            name="cliente"
            value={formData.cliente}
            onChange={handleChange}
            required
            className="w-full border px-3 py-2 rounded"
          >
            <option value="">Selecione um cliente</option>
            {clientes.map(c => (
              <option key={c.id} value={c.id}>
                {c.nome_fantasia}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block mb-1">Empreendimento</label>
          <select
            name="empreendimento"
            value={formData.empreendimento}
            onChange={handleChange}
            required
            disabled={!formData.cliente || loadingEmp}
            className="w-full border px-3 py-2 rounded disabled:opacity-50"
          >
            <option value="">
              {formData.cliente
                ? loadingEmp
                  ? "Carregando..."
                  : "Selecione um empreendimento"
                : "Escolha primeiro o cliente"}
            </option>
            {empreendimentos.map(e => (
              <option key={e.id} value={e.id}>
                {e.nome}
              </option>
            ))}
          </select>
        </div>
        {/* Demais campos do equipamento: nome, marca, modelo, numero_serie, horimetro */}
        <div>
          <label className="block mb-1">Nome</label>
          <input
            name="nome"
            value={formData.nome}
            onChange={handleChange}
            required
            className="w-full border px-3 py-2 rounded"
          />
        </div>
        <div>
          <label className="block mb-1">Marca</label>
          <input
            name="marca"
            value={formData.marca}
            onChange={handleChange}
            required
            className="w-full border px-3 py-2 rounded"
          />
        </div>
        <div>
          <label className="block mb-1">Modelo</label>
          <input
            name="modelo"
            value={formData.modelo}
            onChange={handleChange}
            required
            className="w-full border px-3 py-2.rounded"
          />
        </div>
        <div>
          <label className="block mb-1">Número de Série</label>
          <input
            name="numero_serie"
            value={formData.numero_serie}
            onChange={handleChange}
            required
            className="w-full border px-3 py-2.rounded"
          />
        </div>
        <div>
          <label className="block mb-1">Horímetro</label>
          <input
            type="number"
            step="0.1"
            name="horimetro"
            value={formData.horimetro}
            onChange={handleChange}
            required
            className="w-full border px-3 py-2.rounded"
          />
        </div>
        <button
          type="submit"
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg.green-700"
        >
          Cadastrar Equipamento
        </button>
      </form>
    </div>
  );
}
