import { post } from './index';

export const getGuestTokenReport = async (reportId: string) => {
  const url = `/v1/reports/guest-token`;
  const payload = {
    report_id: reportId
  };

  const { data } = await post({ url, body: payload });
  return data.access_token;
};
