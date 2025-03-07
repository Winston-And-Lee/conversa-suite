export interface IUserInfo {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  created_at: string;
  updated_at: string;
  user_status: number;
  record_name: string;
}

export interface ILoginRequestResponse {
  token: {
    access: string;
    refresh: string;
  };
  user: IUserInfo;
}

export interface IUser {
  id: number;
  name: string;
  workspace: any;
  avatar: string;
}
