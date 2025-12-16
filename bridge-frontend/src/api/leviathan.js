import { apiClient } from "./index";

/**
 * params = {
 *   query: string,
 *   tags?: string[],
 *   planes?: string[], // ["creativity","parser","truth"]
 *   limit?: number
 * }
 */
export const leviathanSearch = (params) =>
  apiClient.post("/engines/leviathan/search", {
    query: params.query,
    tags: params.tags || null,
    planes: params.planes || null,
    limit: Number(params.limit || 50),
  });
