export interface IPermission {
  workspace_id: number;
  resource: string;
  action: string;
  role: string;
  parent?: string;
}
