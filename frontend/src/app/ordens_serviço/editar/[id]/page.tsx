"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

interface OrdemServico {
  id: number;
  cliente: number;
  equipamento: number;
  data_abertura: string;
  descricao: string;
  servicos_realizados: string;
  valor_total: string;
  finalizada: boolean;
  tecnico_responsavel: string;
  anexo?: File | null;
}

interface Cliente {
  id: number;
  nome_fantasia: string;
}

interface Equipamento {
  id: number;
  nome: string;
}

export default function EditarOrdemServicoPage() {
  const params = useParams();
  const id = Array.isArray(params.id) ? params.id[0] : params.id;
  const router = useRouter();
  const [formData, setFormData] = useState<OrdemServico | null>(null);
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [equipamentos, setEquipamentos] = useState<Equipamento[]>([]);
  const [anexoFile, setAnexoFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`https://mandacaru-backend-i2ci.onrender.com/api/ordens-servico/${id}/`)
      .then((res) => res.json())
      .then(setFormData)
      .catch(() => alert("Erro ao carregar dados da ordem."));

    fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/")
      .then((res) => res.json())
      .then(setClientes);

    fetch("https://mandacaru-backend-i2ci.onrender.com/api/equipamentos/")
      .then((res) => res.json())
      .then(setEquipamentos)
      .finally(() => setLoading(false));
  }, [id]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    const newValue = name === "finalizada" ? value === "true" : value;
    setFormData((prev) => prev ? { ...prev, [name]: newValue } : prev);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setAnexoFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData) return;

    const formPayload = new FormData();
    Object.entries(formData).forEach(([key, value]) => {
      formPayload.append(key, value as string);
    });
    if (anexoFile) {
      formPayload.append("anexo", anexoFile);
    }

    const response = await fetch(
      `https://mandacaru-backend-i2ci.onrender.com/api/ordens-servico/${id}/`,
      {
        method: "PUT",
        body: formPayload,
      }
    );

    if (response.ok) {
      alert("Ordem de serviço atualizada com sucesso.");
      router.push("/ordens-servico");
    } else {
      alert("Erro ao atualizar a ordem de serviço.");
    }
  };

  const finalizarViaBot = async () => {
    const confirm = window.confirm("Deseja mesmo finalizar a OS via bot?");
    if (!confirm || !formData) return;

    const response = await fetch(`https://mandacaru-backend-i2ci.onrender.com/api/ordens-servico/${id}/finalizar-bot/`, {
      method: "POST",
    });

    if (response.ok) {
      alert("Solicitação enviada ao bot com sucesso.");
    } else {
      alert("Erro ao comunicar com o bot.");
    }
  };

  if (loading || !formData) return <div className="p-6">Carregando...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Editar Ordem de Serviço</h1>

      <div className="mb-4">
        <span className={`inline-block px-3 py-1 text-sm font-semibold rounded-full
          ${formData.finalizada ? 'bg-green-200 text-green-800' : 'bg-yellow-200 text-yellow-800'}`}>
          {formData.finalizada ? 'Finalizada' : 'Em Aberto'}
        </span>
      </div>

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
          <input type="number" step="0.01" name="valor_total" value={formData.valor_total} onChange={handleChange} className="border p-2 w-full" />
        </label>

        <label className="block">
          Finalizada:
          <select name="finalizada" value={formData.finalizada ? "true" : "false"} onChange={handleChange} className="border p-2 w-full">
            <option value="false">Não</option>
            <option value="true">Sim</option>
          </select>
        </label>

        <label className="block">
          Anexo (PDF ou Imagem):
          <input type="file" accept="image/*,application/pdf" onChange={handleFileChange} className="border p-2 w-full" />
        </label>

        <div className="flex gap-4 mt-6">
          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded">Salvar</button>
          <Link href="/ordens-servico" className="text-blue-500 underline px-4 py-2">Cancelar</Link>
        </div>

        <button type="button" onClick={finalizarViaBot} className="mt-4 bg-blue-600 text-white px-4 py-2 rounded">
          Finalizar via Bot do Telegram
        </button>

        <Link href="/" className="text-sm text-gray-500 underline block mt-6">
          ⬅ Voltar ao Início
        </Link>
      </form>
    </div>
  );
}
