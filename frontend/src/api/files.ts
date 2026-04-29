import apiClient from './client';
import type { FileItem, FileListResponse, FormatsResponse } from '../types';

export async function uploadFile(file: File): Promise<FileItem> {
  const formData = new FormData();
  formData.append('file', file);
  const resp = await apiClient.post<FileItem>('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return resp.data;
}

export async function listFiles(
  page = 1,
  pageSize = 20,
  sort = 'created_at_desc'
): Promise<FileListResponse> {
  const resp = await apiClient.get<FileListResponse>('/files', {
    params: { page, page_size: pageSize, sort },
  });
  return resp.data;
}

export async function getFile(fileId: string): Promise<FileItem> {
  const resp = await apiClient.get<FileItem>(`/files/${fileId}`);
  return resp.data;
}

export async function deleteFile(fileId: string): Promise<void> {
  await apiClient.delete(`/files/${fileId}`);
}

export function getDownloadUrl(fileId: string): string {
  return `/api/v1/files/${fileId}/download`;
}

export async function getFormats(): Promise<FormatsResponse> {
  const resp = await apiClient.get<FormatsResponse>('/files/formats/all');
  return resp.data;
}
