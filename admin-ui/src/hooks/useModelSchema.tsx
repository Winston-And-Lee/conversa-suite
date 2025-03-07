import { HttpError, useApiUrl, useCustom, useResource } from '@refinedev/core';

export const useModelSchema = () => {
  const apiUrl = useApiUrl();
  const { resource } = useResource();
  const { data, isLoading } = useCustom<Object, HttpError>({
    url: `${apiUrl}/${resource?.name}/describe`,
    method: 'get'
  });
  return { schema: data?.data, isLoading };
};
