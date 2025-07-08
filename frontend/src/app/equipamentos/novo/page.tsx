// Correção da página de novo equipamento
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

export default function NovoEquipamentoPage() {
  const router = useRouter();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [empreendimentos, setEmpreendimentos] = useState<Empreendimento[]>([]);
  const [formData, setFormData] = useState({
    nome: "",
    cliente: "",
    empreendimento: "",
    marca: "",
    modelo: "",
    numero_serie: "",
    tipo: "",
    horimetro_atual: "",
    descricao: "",
  });

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/")
      .then((res) => res.json())
      .then((data) => setClientes(data));

    fetch("https://mandacaru-backend-i2ci.onrender.com/api/empreendimentos/")
      .then((res) => res.json())
      .then((data) => setEmpreendimentos(data));
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const response = await fetch("https://mandacaru-backend-i2ci.onrender.com/api/equipamentos/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    if (response.ok) {
      router.push("/equipamentos");
    } else {
      alert("Erro ao cadastrar equipamento");
    }
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4 text-green-700">Novo Equipamento</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input type="text" name="nome" placeholder="Nome" value={formData.nome} onChange={handleChange} className="w-full border p-2 rounded" />

        <select name="cliente" value={formData.cliente} onChange={handleChange} className="w-full border p-2 rounded" required>
          <option value="">Selecione o cliente</option>
          {clientes.map((cliente) => (
            <option key={cliente.id} value={cliente.id}>{cliente.nome_fantasia}</option>
          ))}
        </select>

        <select name="empreendimento" value={formData.empreendimento} onChange={handleChange} className="w-full border p-2 rounded">
          <option value="">Selecione o empreendimento</option>
          {empreendimentos.map((emp) => (
            <option key={emp.id} value={emp.id}>{emp.nome}</option>
          ))}
        </select>

        <input type="text" name="marca" placeholder="Marca" value={formData.marca} onChange={handleChange} className="w-full border p-2 rounded" />
        <input type="text" name="modelo" placeholder="Modelo" value={formData.modelo} onChange={handleChange} className="w-full border p-2 rounded" />
        <input type="text" name="numero_serie" placeholder="Número de Série" value={formData.numero_serie} onChange={handleChange} className="w-full border p-2 rounded" />
        <input type="text" name="tipo" placeholder="Tipo de Equipamento" value={formData.tipo} onChange={handleChange} className="w-full border p-2 rounded" />
        <input type="number" name="horimetro_atual" placeholder="Horímetro Atual" value={formData.horimetro_atual} onChange={handleChange} step="0.1" className="w-full border p-2 rounded" />
        <textarea name="descricao" placeholder="Descrição" value={formData.descricao} onChange={handleChange} className="w-full border p-2 rounded" />

        <div className="flex gap-4 mt-4">
          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">Cadastrar</button>
          <button type="button" onClick={() => router.push("/equipamentos")} className="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500">Cancelar</button>
        </div>
      </form>
    </div>
  );
}
