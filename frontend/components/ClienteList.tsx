'use client'

import { useEffect, useState } from 'react'

interface Cliente {
  id: number
  razao_social: string
  cnpj: string
}

export default function ClienteList({ recarregar }: { recarregar: boolean }) {
  const [clientes, setClientes] = useState<Cliente[]>([])

  useEffect(() => {
    fetch('http://localhost:8000/api/clientes/')
      .then((res) => res.json())
      .then((data) => setClientes(data))
  }, [recarregar])

  return (
    <div className="bg-white p-4 rounded shadow w-full max-w-4xl mx-auto">
      <h2 className="text-xl font-bold mb-4">Lista de Clientes</h2>
      <table className="w-full table-auto border">
        <thead>
          <tr className="bg-gray-200">
            <th className="border px-4 py-2 text-left">Razão Social</th>
            <th className="border px-4 py-2 text-left">CNPJ</th>
          </tr>
        </thead>
        <tbody>
          {clientes.map((cliente) => (
            <tr key={cliente.id}>
              <td className="border px-4 py-2">{cliente.razao_social}</td>
              <td className="border px-4 py-2">{cliente.cnpj}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
