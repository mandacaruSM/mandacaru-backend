'use client';
import { useState, useEffect } from 'react';

import { useRouter } from 'next/navigation';
import { useProdutos } from '@/hooks/useProdutos';

interface ItemRow { produto: number; quantidade: number; preco_unitario: number; subtotal: number; }

export default function NovoOrcamento() {
  const router = useRouter();
  const { resultado, buscar } = useProdutos();
  const [cliente, setCliente] = useState('');
  const [empreendimento, setEmpreendimento] = useState('');
  const [dataVenc, setDataVenc] = useState('');
  const [itens, setItens] = useState<ItemRow[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [distancia, setDistancia] = useState(0);
  const [custoDesloc, setCustoDesloc] = useState(0);

  // buscar empreendimentos
  const [emps, setEmps] = useState<any[]>([]);
  useEffect(() => {
    fetch('/api/empreendimentos/').then(res => res.json()).then(setEmps);
  }, []);

  useEffect(() => {
    if (empreendimento) {
      const emp = emps.find(e => e.id === parseInt(empreendimento));
      setDistancia(emp.distancia_km);
      setCustoDesloc(emp.distancia_km * emp.tarifa_km);
    }
  }, [empreendimento, emps]);

  function adicionarItem(produto: any) {
    setItens(prev => [...prev, {
      produto: produto.id,
      quantidade: 1,
      preco_unitario: produto.preco_unitario,
      subtotal: produto.preco_unitario,
    }]);
    setSearchTerm('');
    setResultado([]);
  }

  function atualizarQtd(idx: number, qtd: number) {
    setItens(prev => {
      const newIt = [...prev];
      newIt[idx].quantidade = qtd;
      newIt[idx].subtotal = qtd * newIt[idx].preco_unitario;
      return newIt;
    });
  }

  const totalItens = itens.reduce((s, i) => s + i.subtotal, 0);
  const total = totalItens + custoDesloc;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const payload = { cliente, empreendimento, data_vencimento: dataVenc, itens, status: 'PENDENTE' };
    await fetch('/api/orcamentos/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    router.push('/orcamentos');
  }

  return (
    <Layout>
      <h1 className="text-2xl font-bold mb-4">Novo Orçamento</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div><label>Cliente</label><input value={cliente} onChange={e => setCliente(e.target.value)} required className="w-full" /></div>
          <div><label>Empreendimento</label>
            <select value={empreendimento} onChange={e => setEmpreendimento(e.target.value)} required className="w-full">
              <option value="">Selecione</option>
              {emps.map(e => <option key={e.id} value={e.id}>{e.nome}</option>)}
            </select>
          </div>
          <div><label>Data Vencimento</label><input type="date" value={dataVenc} onChange={e => setDataVenc(e.target.value)} required className="w-full" /></div>
        </div>

        <div>
          <label>Buscar Item</label>
          <input
            value={searchTerm}
            onChange={e => { setSearchTerm(e.target.value); buscar(e.target.value); }}
            className="w-full"
          />
          {resultado.length > 0 && (
            {
              resultado.map(p => (
                <li key={p.id} onClick={() => adicionarItem(p)} className="p-2 hover:bg-gray-100 cursor-pointer">
                  {p.nome} - R$ {p.preco_unitario.toFixed(2)}
                </li>
              ))
            }
            </ul>
          )}
      </div>

      <table className="w-full table-auto mb-4">
        <thead><tr><th>Produto</th><th>Qtd</th><th>Unit</th><th>Subtotal</th></tr></thead>
        <tbody>
          {itens.map((it, i) => (
            <tr key={i}>
              <td>{it.produto}</td>
              <td><input type="number" value={it.quantidade} min={1} onChange={e => atualizarQtd(i, parseFloat(e.target.value))} className="w-16" /></td>
              <td>R$ {it.preco_unitario.toFixed(2)}</td>
              <td>R$ {it.subtotal.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="space-y-1">
        <p>Total Itens: R$ {totalItens.toFixed(2)}</p>
        <p>Deslocamento ({distancia} km): R$ {custoDesloc.toFixed(2)}</p>
        <p className="font-bold">Total Orçamento: R$ {total.toFixed(2)}</p>
      </div>

      <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">Salvar Orçamento</button>
    </form>
    </Layout >
  );
} <ul className="border max-h-32 overflow-auto">
