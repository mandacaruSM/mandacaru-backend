"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

interface Cliente {
  id: number;
  nome_fantasia: string;
}

interface Fornecedor {
  id: number;
  nome_fantasia: string;
}

export default function NovaContaPage() {
  const router = useRouter();
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [fornecedores, setFornecedores] = useState<Fornecedor[]>([]);
  const [formData, setFormData] = useState({
    descricao: "",
    valor: "",
    data_vencimento: "",
    forma_pagamento: "",
    tipo: "pagar",
    status: "pendente",
    cliente: "",
    fornecedor: "",
    comprovante: null as File | null,
  });

  useEffect(() => {
    axios.get<Cliente[]>("https://mandacaru-backend-i2ci.onrender.com/api/clientes/")
      .then((res) => setClientes(res.data));
    axios.get<Fornecedor[]>("https://mandacaru-backend-i2ci.onrender.com/api/fornecedores/")
      .then((res) => setFornecedores(res.data));
  }, []);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFormData((prev) => ({ ...prev, comprovante: e.target.files![0] }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const valorFloat = parseFloat(formData.valor.replace(",", "."));
    if (isNaN(valorFloat) || valorFloat <= 0) {
      alert("Valor inválido");
      return;
    }

    const data = new FormData();
    data.append("descricao", formData.descricao);
    data.append("valor", valorFloat.toString());
    data.append("data_vencimento", formData.data_vencimento);
    data.append("forma_pagamento", formData.forma_pagamento);
    data.append("tipo", formData.tipo);
    data.append("status", formData.status);
    if (formData.cliente) data.append("cliente", formData.cliente);
    if (formData.fornecedor) data.append("fornecedor", formData.fornecedor);
    if (formData.comprovante) data.append("comprovante", formData.comprovante);

    try {
      await axios.post("https://mandacaru-backend-i2ci.onrender.com/api/financeiro/contas/", data);
      router.push("/financeiro");
    } catch (error) {
      console.error("Erro ao salvar conta:", error);
      alert("Erro ao salvar. Verifique os dados.");
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-green-800 mb-4">Nova Conta</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input name="descricao" placeholder="Descrição" onChange={handleChange} required className="w-full p-2 border rounded" />
        <input name="valor" placeholder="Valor" type="number" onChange={handleChange} required className="w-full p-2 border rounded" />
        <input name="data_vencimento" type="date" onChange={handleChange} required className="w-full p-2 border rounded" />
        <input name="forma_pagamento" placeholder="Forma de Pagamento" onChange={handleChange} className="w-full p-2 border rounded" />
        <select name="tipo" onChange={handleChange} className="w-full p-2 border rounded">
          <option value="pagar">Pagar</option>
          <option value="receber">Receber</option>
        </select>
        <select name="status" onChange={handleChange} className="w-full p-2 border rounded">
          <option value="pendente">Pendente</option>
          <option value="pago">Pago</option>
        </select>
        <select name="cliente" onChange={handleChange} className="w-full p-2 border rounded">
          <option value="">Selecione o Cliente (opcional)</option>
          {clientes.map((c) => (
            <option key={c.id} value={c.id}>{c.nome_fantasia}</option>
          ))}
        </select>
        <select name="fornecedor" onChange={handleChange} className="w-full p-2 border rounded">
          <option value="">Selecione o Fornecedor (opcional)</option>
          {fornecedores.map((f) => (
            <option key={f.id} value={f.id}>{f.nome_fantasia}</option>
          ))}
        </select>
        <input type="file" accept="image/*,application/pdf" onChange={handleFileChange} className="w-full p-2 border rounded" />
        <div className="flex gap-4">
          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
            Salvar
          </button>
          <button type="button" onClick={() => router.push("/financeiro")} className="bg-gray-400 text-white px-4 py-2 rounded hover:bg-gray-500">
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
}
