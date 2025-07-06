"use client";

import Link from "next/link";

export default function TopBar({ titulo }: { titulo: string }) {
  return (
    <div className="flex justify-between items-center mb-4 border-b pb-2">
      <h1 className="text-2xl font-bold text-green-800">{titulo}</h1>
      <Link
        href="/"
        className="bg-gray-300 text-gray-800 px-3 py-1 rounded hover:bg-gray-400"
      >
        🏠 Início
      </Link>
    </div>
  );
}
