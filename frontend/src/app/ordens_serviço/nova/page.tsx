"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface Cliente {
  id: number;
  nome_fantasia: string;
}

interface Equipamento {
  id: number;
  nome: string;
}

export default function NovaOrdemServicoPage() {
  const router = useRouter();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [equipamentos, setEquipamentos] = useState<Equipamento[]>([]);
  const [anexoFile, setAnexoFile] = useState<File | null>(null);
  const [formData, setFormData] = useState({
    cliente: "",
    equipamento: "",
    data_abertura: "",
    tecnico_responsavel: "",
    descricao: "",
    servicos_realizados: "",
    valor_total: "",
    finalizada: false,
  });

  useEffect(() => {
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/")
      .then((res) => res.json())
      .then(setClientes);
    fetch("https://mandacaru-backend-i2ci.onrender.com/api/equipamentos/")
      .then((res) => res.json())
      .then(setEquipamentos);
  }, []);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: name === "finalizada" ? value === "true" : value });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setAnexoFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const payload = new FormData();
    Object.entries(formData).forEach(([key, value]) => {
      payload.append(key, value.toString());
    });
    if (anexoFile) {
      payload.append("anexo", anexoFile);
    }

    const response = await fetch("https://mandacaru-backend-i2ci.onrender.com/api/ordens-servico/", {
      method: "POST",
      body: payload,
    });

    if (response.ok) {
      alert("Ordem de serviço criada com sucesso.");
      router.push("/ordens-servico");
    } else {
      alert("Erro ao criar ordem de serviço.");
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4 text-green-800">Nova Ordem de Serviço</h1>
      <form onSubmit={handleSubmit} className="space-y-4" encType="multipart/form-data">

        <label className="block">
          Cliente:
          <select name="cliente" value={formData.cliente} onChange={handleChange} className="border p-2 w-full" required>
            <option value="">Selecione</option>
            {clientes.map((cliente) => (
              <option key={cliente.id} value={cliente.id}>{cliente.nome_fantasia}</option>
            ))}
          </select>
        </label>

        <label className="block">
          Equipamento:
          <select name="equipamento" value={formData.equipamento} onChange={handleChange} className="border p-2 w-full" required>
            <option value="">Selecione</option>
            {equipamentos.map((eq) => (
              <option key={eq.id} value={eq.id}>{eq.nome}</option>
            ))}
          </select>
        </label>

        <label className="block">
          Data de Abertura:
          <input type="date" name="data_abertura" value={formData.data_abertura} onChange={handleChange} className="border p-2 w-full" required />
        </label>

        <label className="block">
          Técnico Responsável:
          <input type="text" name="tecnico_responsavel" value={formData.tecnico_responsavel} onChange={handleChange} className="border p-2 w-full" />
        </label>

        <label className="block">
          Descrição:
          <textarea name="descricao" value={formData.descricao} onChange={handleChange} className="border p-2 w-full" />
        </label>

        <label className="block">
          Serviços Realizados:
          <textarea name="servicos_realizados" value={formData.servicos_realizados} onChange={handleChange} className="border p-2 w-full" />
        </label>

        <label className="block">
          Valor Total (R$):
          <input type="number" name="valor_total" value={formData.valor_total} onChange={handleChange} className="border p-2 w-full" step="0.01" />
        </label>

        <label className="block">
          Anexo (PDF ou imagem):
          <input type="file" accept="application/pdf,image/*" onChange={handleFileChange} className="border p-2 w-full" />
        </label>

        <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded">Salvar</button>
        <Link href="/ordens-servico" className="ml-4 text-blue-500 underline">Cancelar</Link>
      </form>
    </div>
  );
}
