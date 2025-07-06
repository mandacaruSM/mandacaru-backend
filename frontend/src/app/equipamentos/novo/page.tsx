"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Link from "next/link";

interface Cliente {
  id: number;
  nome_fantasia: string;
}

interface Empreendimento {
  id: number;
  nome: string;
}

export default function NovoEquipamento() {
  const router = useRouter();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [empreendimentos, setEmpreendimentos] = useState<Empreendimento[]>([]);
  const [formData, setFormData] = useState({
    nome: "",
    tipo: "",
    fabricante: "",
    modelo: "",
    numero_serie: "",
    cliente: "",
    empreendimento: "",
    observacoes: "",
  });

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/")
      .then((res) => res.json())
      .then(setClientes);

    fetch("https://mandacaru-backend-i2ci.onrender.com/api/empreendimentos/")
      .then((res) => res.json())
      .then(setEmpreendimentos);
  }, []);

  const handleChange = (e: any) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    await fetch("https://mandacaru-backend-i2ci.onrender.com/api/equipamentos/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });
    router.push("/equipamentos");
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-green-800">Novo Equipamento</h2>
        <Link href="/" className="bg-gray-300 text-gray-800 px-3 py-1 rounded hover:bg-gray-400">
          🏠 Home
        </Link>
      </div>
      <form onSubmit={handleSubmit} className="grid gap-4">
        <input name="nome" placeholder="Nome" onChange={handleChange} className="border rounded p-2" required />
        <input name="tipo" placeholder="Tipo" onChange={handleChange} className="border rounded p-2" />
        <input name="fabricante" placeholder="Fabricante" onChange={handleChange} className="border rounded p-2" />
        <input name="modelo" placeholder="Modelo" onChange={handleChange} className="border rounded p-2" />
        <input name="numero_serie" placeholder="Número de Série" onChange={handleChange} className="border rounded p-2" />
        
        <select name="cliente" onChange={handleChange} className="border rounded p-2">
          <option value="">Selecione um Cliente</option>
          {clientes.map((c) => <option key={c.id} value={c.id}>{c.nome_fantasia}</option>)}
        </select>

        <select name="empreendimento" onChange={handleChange} className="border rounded p-2">
          <option value="">Selecione um Empreendimento</option>
          {empreendimentos.map((e) => <option key={e.id} value={e.id}>{e.nome}</option>)}
        </select>

        <textarea name="observacoes" placeholder="Observações" onChange={handleChange} className="border rounded p-2" />

        <button type="submit" className="bg-green-700 text-white px-4 py-2 rounded hover:bg-green-800">
          Salvar
        </button>
      </form>
    </div>
  );
}
