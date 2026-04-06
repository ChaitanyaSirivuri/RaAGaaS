import ky, { type KyInstance } from "ky";

import { useAppStore } from "@/store/appStore";

const API_PREFIX = import.meta.env.VITE_API_BASE_URL ?? "";

function getApiKey(): string {
  return useAppStore.getState().apiKey ?? "";
}

export const api: KyInstance = ky.create({
  prefixUrl: API_PREFIX,
  hooks: {
    beforeRequest: [
      (request) => {
        const key = getApiKey();
        if (key) {
          request.headers.set("Authorization", `Bearer ${key}`);
        }
      },
    ],
  },
});

export type Collection = {
  id: string;
  tenant_id: string;
  name: string;
  embedding_model: string;
  chunk_strategy: string;
  chunk_size: number;
  chunk_overlap: number;
  weaviate_class: string;
  created_at: string;
  document_count?: number;
};

export type DocumentRow = {
  id: string;
  collection_id: string;
  filename: string;
  status: string;
  chunk_count: number;
  created_at: string;
};

export type ApiKeyRow = {
  id: string;
  key_prefix: string;
  scopes: string[];
  expires_at: string | null;
  created_at: string;
};

export type QueryResultItem = { text: string; score: number; metadata: Record<string, unknown> };

export async function fetchCollections(): Promise<Collection[]> {
  return api.get("v1/collections").json();
}

export async function createCollection(body: {
  name: string;
  chunk_strategy?: string;
  chunk_size?: number;
  chunk_overlap?: number;
  embedding_model?: string | null;
}): Promise<Collection> {
  return api.post("v1/collections", { json: body }).json();
}

export async function fetchCollection(id: string): Promise<Collection & { document_count: number }> {
  return api.get(`v1/collections/${id}`).json();
}

export async function fetchDocuments(collectionId: string): Promise<DocumentRow[]> {
  return api.get(`v1/collections/${collectionId}/documents`).json();
}

export async function uploadDocument(collectionId: string, file: File): Promise<DocumentRow> {
  const form = new FormData();
  form.append("file", file);
  return api.post(`v1/collections/${collectionId}/documents`, { body: form }).json();
}

export async function runQuery(
  collectionId: string,
  query: string,
  top_k = 5,
): Promise<{ results: QueryResultItem[]; latency_ms: number }> {
  return api
    .post(`v1/collections/${collectionId}/query`, {
      json: { query, top_k, include_metadata: true },
    })
    .json();
}

export async function runChat(
  collectionId: string,
  messages: { role: string; content: string }[],
  top_k = 5,
): Promise<{ answer: string; sources: { filename?: string | null; excerpt: string; chunk_index?: number | null }[] }> {
  return api.post(`v1/collections/${collectionId}/chat`, { json: { messages, top_k } }).json();
}

export async function listKeys(): Promise<ApiKeyRow[]> {
  return api.get("v1/keys").json();
}

export async function createKey(scopes: string[]): Promise<{ id: string; key: string; key_prefix: string }> {
  return api.post("v1/keys", { json: { scopes } }).json();
}

export type TableSchema = { name: string; columns: { name: string; type: string }[] };

export async function registerDbSource(label: string, connectionUri?: string, file?: File): Promise<{ id: string }> {
  const form = new FormData();
  form.append("label", label);
  if (connectionUri) {
    form.append("connection_uri", connectionUri);
  }
  if (file) {
    form.append("file", file);
  }
  return api.post("v1/db-sources", { body: form }).json();
}

export async function fetchDbSchema(sourceId: string): Promise<{ tables: TableSchema[] }> {
  return api.get(`v1/db-sources/${sourceId}/schema`).json();
}

export async function startDbImport(
  sourceId: string,
  collectionId: string,
  selections: {
    table: string;
    columns: { column: string; use_as_text: boolean; store_as_metadata: boolean }[];
  }[],
): Promise<{ id: string; status: string; rows_processed: number }> {
  return api
    .post(`v1/db-sources/${sourceId}/import`, {
      json: { collection_id: collectionId, selections },
    })
    .json();
}

export async function fetchImportJob(
  sourceId: string,
  jobId: string,
): Promise<{ id: string; status: string; rows_processed: number }> {
  return api.get(`v1/db-sources/${sourceId}/import/${jobId}`).json();
}
