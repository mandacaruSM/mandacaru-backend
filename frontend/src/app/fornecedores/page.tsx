"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import axios from "axios";

interface Fornecedor {
  id: number;
  nome_fantasia: string;
  cnpj?: string;
  telefone?: string;
  email?: string;
}

export default function FornecedoresPage() {
  const [fornecedores, setFornecedores] = useState<Fornecedor[]>([]);

  useEffect(() => {
    axios.get<Fornecedor[]>("https://mandacaru-backend-i2ci.onrender.com/api/fornecedores/")
      .then((res) => setFornecedores(res.data))
  }, []);

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-green-800">Fornecedores</h1>
        <Link href="/fornecedores/novo" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
          Novo Fornecedor
        </Link>
      </div>

      <table className="w-full bg-white border shadow rounded text-sm">
        <thead className="bg-gray-100">
          <tr>
            <th className="p-2 text-left">Nome Fantasia</th>
            <th className="p-2 text-left">CNPJ</th>
            <th className="p-2 text-left">Telefone</th>
            <th className="p-2 text-left">E-mail</th>
            <th className="p-2 text-left">Ações</th>
          </tr>
        </thead>
        <tbody>
          {fornecedores.map((f) => (
            <tr key={f.id} className="border-t">
              <td className="p-2">{f.nome_fantasia}</td>
              <td className="p-2">{f.cnpj || "-"}</td>
              <td className="p-2">{f.telefone || "-"}</td>
              <td className="p-2">{f.email || "-"}</td>
              <td className="p-2">
                <Link
                  href={`/fornecedores/editar/${f.id}`}
                  className="text-blue-600 hover:underline"
                >
                  Editar
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
