"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

interface Cliente {
  id: number;
  nome_fantasia: string;
}

interface Empreendimento {
  id: number;
  nome: string;
  cliente: number;
}

interface Equipamento {
  id: number;
  nome: string;
  cliente: number;
  empreendimento: number;
}

export default function EditarManutencaoPage() {
  const { id } = useParams();
  const router = useRouter();

  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [empreendimentos, setEmpreendimentos] = useState<Empreendimento[]>([]);
  const [equipamentos, setEquipamentos] = useState<Equipamento[]>([]);

  const [formData, setFormData] = useState({
    cliente: "",
    empreendimento: "",
    equipamento: "",
    tipo: "preventiva",
    data: "",
    horimetro: "",
    tecnico_responsavel: "",
    descricao: "",
    observacoes: "",
    proxima_manutencao: "",
  });

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/")
      .then((res) => res.json())
      .then(setClientes);

    fetch("https://mandacaru-backend-i2ci.onrender.com/api/manutencoes/" + id + "/")
      .then((res) => res.json())
      .then((data) => {
        setFormData({
          cliente: data.equipamento.cliente.toString(),
          empreendimento: data.equipamento.empreendimento.toString(),
          equipamento: data.equipamento.id.toString(),
          tipo: data.tipo,
          data: data.data,
          horimetro: data.horimetro,
          tecnico_responsavel: data.tecnico_responsavel,
          descricao: data.descricao,
          observacoes: data.observacoes || "",
          proxima_manutencao: data.proxima_manutencao || "",
        });
      });
  }, [id]);

  useEffect(() => {
    if (formData.cliente) {
      fetch(`https://mandacaru-backend-i2ci.onrender.com/api/empreendimentos/?cliente=${formData.cliente}`)
        .then((res) => res.json())
        .then(setEmpreendimentos);
    }
  }, [formData.cliente]);

  useEffect(() => {
    if (formData.empreendimento) {
      fetch(`https://mandacaru-backend-i2ci.onrender.com/api/equipamentos/?empreendimento=${formData.empreendimento}`)
        .then((res) => res.json())
        .then(setEquipamentos);
    }
  }, [formData.empreendimento]);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await fetch(`https://mandacaru-backend-i2ci.onrender.com/api/manutencoes/${id}/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });
    router.push("/manutencoes");
  };

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold text-green-800 mb-4">Editar Manutenção</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <select name="cliente" value={formData.cliente} onChange={handleChange} className="w-full border rounded p-2" required>
          <option value="">Selecione o cliente</option>
          {clientes.map((c) => (
            <option key={c.id} value={c.id}>
              {c.nome_fantasia}
            </option>
          ))}
        </select>

        <select name="empreendimento" value={formData.empreendimento} onChange={handleChange} className="w-full border rounded p-2" required>
          <option value="">Selecione o empreendimento</option>
          {empreendimentos.map((e) => (
            <option key={e.id} value={e.id}>
              {e.nome}
            </option>
          ))}
        </select>

        <select name="equipamento" value={formData.equipamento} onChange={handleChange} className="w-full border rounded p-2" required>
          <option value="">Selecione o equipamento</option>
          {equipamentos.map((e) => (
            <option key={e.id} value={e.id}>
              {e.nome}
            </option>
          ))}
        </select>

        <select name="tipo" value={formData.tipo} onChange={handleChange} className="w-full border rounded p-2">
          <option value="preventiva">Preventiva</option>
          <option value="corretiva">Corretiva</option>
        </select>

        <input type="date" name="data" value={formData.data} onChange={handleChange} className="w-full border rounded p-2" required />
        <input type="number" step="0.01" name="horimetro" value={formData.horimetro} onChange={handleChange} placeholder="Horímetro" className="w-full border rounded p-2" required />
        <input type="text" name="tecnico_responsavel" value={formData.tecnico_responsavel} onChange={handleChange} placeholder="Técnico Responsável" className="w-full border rounded p-2" />
        <textarea name="descricao" value={formData.descricao} onChange={handleChange} placeholder="Descrição" className="w-full border rounded p-2"></textarea>
        <textarea name="observacoes" value={formData.observacoes} onChange={handleChange} placeholder="Observações" className="w-full border rounded p-2"></textarea>
        {formData.tipo === "preventiva" && (
          <input type="date" name="proxima_manutencao" value={formData.proxima_manutencao} onChange={handleChange} className="w-full border rounded p-2" placeholder="Próxima Manutenção" />
        )}
        <div className="flex justify-between">
          <button type="button" onClick={() => router.push("/manutencoes")} className="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500">Voltar</button>
          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">Salvar Alterações</button>
        </div>
      </form>
    </div>
  );
}
