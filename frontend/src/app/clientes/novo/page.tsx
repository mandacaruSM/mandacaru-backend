"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function NovoCliente() {
  const router = useRouter();

  const [formData, setFormData] = useState({
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
        const errorData = await res.json();
        alert("Erro ao cadastrar cliente:\n" + JSON.stringify(errorData, null, 2));
      }
    } catch (error) {
      alert("Erro ao conectar com o servidor.");
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-4 text-green-800">Novo Cliente</h2>
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[
          { name: "razao_social", label: "Razão Social" },
          { name: "nome_fantasia", label: "Nome Fantasia" },
          { name: "cnpj", label: "CNPJ" },
          { name: "inscricao_estadual", label: "Inscrição Estadual" },
          { name: "email", label: "Email" },
          { name: "telefone", label: "Telefone" },
          { name: "rua", label: "Rua" },
          { name: "numero", label: "Número" },
          { name: "bairro", label: "Bairro" },
          { name: "cidade", label: "Cidade" },
          { name: "estado", label: "Estado" },
          { name: "cep", label: "CEP" },
        ].map((field) => (
          <div key={field.name}>
            <label className="block text-sm font-medium mb-1" htmlFor={field.name}>
              {field.label}
            </label>
            <input
              type="text"
              name={field.name}
              value={(formData as any)[field.name]}
              onChange={handleChange}
              className="w-full border px-3 py-2 rounded"
              required={field.name === "razao_social" || field.name === "cnpj" || field.name === "rua"}
            />
          </div>
        ))}

        <div className="md:col-span-2">
          <label className="block text-sm font-medium mb-1" htmlFor="observacoes">
            Observações
          </label>
          <textarea
            name="observacoes"
            value={formData.observacoes}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded"
            rows={4}
          />
        </div>

        <div className="md:col-span-2 flex justify-end mt-4">
          <button type="submit" className="bg-green-700 text-white px-6 py-2 rounded hover:bg-green-800">
            Salvar Cliente
          </button>
        </div>
      </form>
    </div>
  );
}
