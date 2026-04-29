import apiClient from './client';
import type {
  ConversionStartRequest,
  BatchStartResponse,
  TaskResponse,
  BatchStatusResponse,
} from '../types';

export async function startConversion(
  request: ConversionStartRequest
): Promise<BatchStartResponse> {
  const resp = await apiClient.post<BatchStartResponse>(
    '/conversion/start',
    request
  );
  return resp.data;
}

export async function getTask(taskId: string): Promise<TaskResponse> {
  const resp = await apiClient.get<TaskResponse>(`/conversion/task/${taskId}`);
  return resp.data;
}

export async function getBatch(batchId: string): Promise<BatchStatusResponse> {
  const resp = await apiClient.get<BatchStatusResponse>(
    `/conversion/batch/${batchId}`
  );
  return resp.data;
}

export async function cancelTask(taskId: string): Promise<TaskResponse> {
  const resp = await apiClient.post<TaskResponse>(
    `/conversion/task/${taskId}/cancel`
  );
  return resp.data;
}
