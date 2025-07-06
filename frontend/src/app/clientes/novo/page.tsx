"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import Link from "next/link";

interface Cliente {
  razao_social: string;
  nome_fantasia?: string;
  cnpj: string;
  inscricao_estadual?: string;
  email?: string;
  telefone?: string;
  rua: string;
  numero: string;
  bairro: string;
  cidade: string;
  estado: string;
  cep: string;
  observacoes?: string;
}

export default function NovoCliente() {
  const router = useRouter();
  const [formData, setFormData] = useState<Cliente>({
    razao_social: "",
    nome_fantasia: "",
    cnpj: "",
    inscricao_estadual: "",
    email: "",
    telefone: "",
    rua: "",
    numero: "",
    bairro: "",
    cidade: "",
    estado: "",
    cep: "",
    observacoes: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch("https://mandacaru-backend-i2ci.onrender.com/api/clientes/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      if (res.ok) {
        alert("Cliente cadastrado com sucesso!");
        router.push("/clientes");
      } else {
        const erro = await res.json();
        alert("Erro: " + JSON.stringify(erro));
      }
    } catch {
      alert("Erro ao salvar.");
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold">Novo Cliente</h2>
        <Link href="/" className="bg-gray-200 text-gray-800 px-3 py-1 rounded hover:bg-gray-300">
          🏠 Home
        </Link>
      </div>
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {Object.entries(formData).map(([campo, valor]) => (
          <div key={campo} className="col-span-1">
            <label className="block text-sm font-medium capitalize mb-1">
              {campo.replace("_", " ")}
            </label>
            {campo === "observacoes" ? (
              <textarea
                name={campo}
                className="w-full border px-2 py-1 text-sm rounded"
                value={valor}
                onChange={handleChange}
              />
            ) : (
              <input
                name={campo}
                type="text"
                className="w-full border px-2 py-1 text-sm rounded"
                value={valor}
                onChange={handleChange}
              />
            )}
          </div>
        ))}
        <div className="col-span-2">
          <button
            type="submit"
            className="bg-green-700 text-white px-4 py-2 rounded hover:bg-green-800 w-full md:w-auto"
          >
            Cadastrar
          </button>
        </div>
      </form>
    </div>
  );
}
