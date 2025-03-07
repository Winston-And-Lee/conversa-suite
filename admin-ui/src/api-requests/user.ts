import { get } from '@/api-requests/';

export const getUser = async (user_id: number) => {
  const response = await get({
    url: `/v1/users/${user_id}`
  });

  return response;
};
