import apiClient from './client';
import type { MetadataResponse, MetadataUpdate } from '../types';

export async function getMetadata(fileId: string): Promise<MetadataResponse> {
  const resp = await apiClient.get<MetadataResponse>(
    `/metadata/${fileId}`
  );
  return resp.data;
}

export async function updateMetadata(
  fileId: string,
  data: MetadataUpdate
): Promise<MetadataResponse> {
  const resp = await apiClient.put<MetadataResponse>(
    `/metadata/${fileId}`,
    data
  );
  return resp.data;
}

export async function uploadCover(
  fileId: string,
  file: File
): Promise<{ cover_url: string }> {
  const formData = new FormData();
  formData.append('cover', file);
  const resp = await apiClient.post<{ cover_url: string }>(
    `/metadata/${fileId}/cover`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  );
  return resp.data;
}
