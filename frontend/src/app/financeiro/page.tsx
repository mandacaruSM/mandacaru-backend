"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import axios from "axios";

interface Conta {
  id: number;
  descricao: string;
  valor: number;
  vencimento: string;
  forma_pagamento: string;
  tipo: string;
  status: string;
  cliente_nome?: string;
  fornecedor_nome?: string;
  comprovante?: string;
}

export default function FinanceiroPage() {
  const [contas, setContas] = useState<Conta[]>([]);

  useEffect(() => {
    axios.get<Conta[]>("https://mandacaru-backend-i2ci.onrender.com/api/financeiro/contas/")
      .then((res) => setContas(res.data))
      .catch((err) => console.error("Erro ao carregar contas:", err));
  }, []);

  const formatarValor = (valor: number) =>
    new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(valor);

  const marcarComoPago = async (id: number) => {
    const confirmar = confirm("Deseja realmente dar baixa nesta conta?");
    if (!confirmar) return;

    try {
      await axios.patch(`https://mandacaru-backend-i2ci.onrender.com/api/financeiro/contas/${id}/`, {
        status: "pago",
      });

      setContas((prev) =>
        prev.map((conta) =>
          conta.id === id ? { ...conta, status: "pago" } : conta
        )
      );
    } catch (err) {
      console.error("Erro ao dar baixa:", err);
      alert("Erro ao tentar dar baixa na conta.");
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold text-green-800">Contas Financeiras</h1>
        <Link href="/financeiro/novo" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
          Nova Conta
        </Link>
      </div>

      {contas.length === 0 ? (
        <p className="text-gray-600">Nenhuma conta cadastrada.</p>
      ) : (
        <table className="min-w-full bg-white shadow rounded">
          <thead>
            <tr className="bg-gray-100">
              <th className="p-2 text-left">Descrição</th>
              <th className="p-2 text-left">Valor</th>
              <th className="p-2 text-left">Vencimento</th>
              <th className="p-2 text-left">Tipo</th>
              <th className="p-2 text-left">Status</th>
              <th className="p-2 text-left">Cliente/Fornecedor</th>
              <th className="p-2 text-left">Comprovante</th>
              <th className="p-2 text-left">Ações</th>
            </tr>
          </thead>
          <tbody>
            {contas.map((conta) => (
              <tr key={conta.id} className="border-b">
                <td className="p-2">{conta.descricao}</td>
                <td className="p-2">{formatarValor(conta.valor)}</td>
                <td className="p-2">{conta.vencimento}</td>
                <td className="p-2 capitalize">{conta.tipo}</td>
                <td className="p-2 capitalize">{conta.status}</td>
                <td className="p-2">{conta.cliente_nome || conta.fornecedor_nome || "-"}</td>
                <td className="p-2">
                  {conta.comprovante ? (
                    <a href={conta.comprovante} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Ver</a>
                  ) : "-"}
                </td>
                <td className="p-2 space-x-2">
                  <Link href={`/financeiro/editar/${conta.id}`} className="text-blue-600 hover:underline">Editar</Link>
                  {conta.status === "pendente" && (
                    <button onClick={() => marcarComoPago(conta.id)} className="text-green-600 hover:underline">Pagar</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
