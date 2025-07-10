// src/hooks/useProdutos.ts
import { useState } from 'react';

export function useProdutos() {
  const [resultado, setResultado] = useState<any[]>([]);

  async function buscar(query: string) {
    const res = await fetch(`/api/almoxarifado/produtos/?search=${query}`);
    const data = await res.json();
    setResultado(data);
  }

  return { resultado, buscar };
}