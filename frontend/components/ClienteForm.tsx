// components/ClienteForm.tsx
"use client"

import { useEffect, useState } from "react";

interface Cliente {
  id: number;
  razao_social: string;
  nome_fantasia: string;
}

type ClienteFormData = {
  razao_social: string;
  nome_fantasia: string;
  cnpj: string;
  inscricao_estadual: string;
  telefone: string;
  email: string;
  rua: string;
  numero: string;
  bairro: string;
  cidade: string;
  estado: string;
  cep: string;
  observacoes: string;
};

export default function ClienteForm() {
  const [formData, setFormData] = useState<ClienteFormData>({
    razao_social: "",
    nome_fantasia: "",
    cnpj: "",
    inscricao_estadual: "",
    telefone: "",
    email: "",
    rua: "",
    numero: "",
    bairro: "",
    cidade: "",
    estado: "",
    cep: "",
    observacoes: ""
  });

  const [clientes, setClientes] = useState<Cliente[]>([]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      const res = await fetch(`${apiUrl}/api/clientes/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)
      });
      if (res.ok) {
        alert("Cliente cadastrado com sucesso!");
        setFormData({
          razao_social: "",
          nome_fantasia: "",
          cnpj: "",
          inscricao_estadual: "",
          telefone: "",
          email: "",
          rua: "",
          numero: "",
          bairro: "",
          cidade: "",
          estado: "",
          cep: "",
          observacoes: ""
        });
        fetchClientes();
      } else {
        alert("Erro ao cadastrar cliente.");
      }
    } catch (error) {
      alert("Erro na requisição: " + error);
    }
  };

  const fetchClientes = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      const res = await fetch(`${apiUrl}/api/clientes/`);
      if (res.ok) {
        const data = await res.json();
        setClientes(data);
      }
    } catch (error) {
      console.error("Erro ao buscar clientes:", error);
    }
  };

  useEffect(() => {
    fetchClientes();
  }, []);

  return (
    <div className="bg-gray-900 text-white min-h-screen p-4">
      <form onSubmit={handleSubmit} className="space-y-4 bg-gray-800 p-6 rounded-xl shadow-lg max-w-md mx-auto">
        <h2 className="text-2xl font-bold mb-4">Cadastrar Cliente</h2>
        {[
          { name: "razao_social", label: "Razão Social" },
          { name: "nome_fantasia", label: "Nome Fantasia" },
          { name: "cnpj", label: "CNPJ" },
          { name: "inscricao_estadual", label: "Inscrição Estadual" },
          { name: "telefone", label: "Telefone" },
          { name: "email", label: "E-mail" },
          { name: "rua", label: "Rua" },
          { name: "numero", label: "Número" },
          { name: "bairro", label: "Bairro" },
          { name: "cidade", label: "Cidade" },
          { name: "estado", label: "Estado" },
          { name: "cep", label: "CEP" }
        ].map(({ name, label }) => (
          <div key={name}>
            <label className="block text-sm font-medium mb-1">{label}</label>
            <input
              name={name}
              value={formData[name as keyof ClienteFormData]}
              onChange={handleChange}
              required={name !== "inscricao_estadual" && name !== "numero" && name !== "observacoes"}
              className="w-full p-2 rounded-md bg-gray-700 border border-gray-600 text-white"
            />
          </div>
        ))}
        <div>
          <label className="block text-sm font-medium mb-1">Observações</label>
          <textarea
            name="observacoes"
            value={formData.observacoes}
            onChange={handleChange}
            className="w-full p-2 rounded-md bg-gray-700 border border-gray-600 text-white"
          ></textarea>
        </div>
        <button type="submit" className="bg-blue-600 text-white w-full py-2 rounded-md hover:bg-blue-700">
          Salvar Cliente
        </button>
      </form>

      {/* Listagem de clientes */}
      <div className="mt-8 max-w-md mx-auto space-y-4">
        <h3 className="text-xl font-semibold">Clientes Cadastrados</h3>
        {clientes.length === 0 ? (
          <p className="text-gray-400">Nenhum cliente cadastrado.</p>
        ) : (
          clientes.map(cliente => (
            <div key={cliente.id} className="bg-gray-800 p-4 rounded-md border border-gray-700">
              <p className="font-bold">{cliente.razao_social}</p>
              <p className="text-sm text-gray-300">{cliente.nome_fantasia}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
