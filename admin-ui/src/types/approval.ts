export interface Approval {
  id: string;
  approval_group_id: number;
  name: string;
  description: string;
  datatable_schema_id: string;
  datatable_schema_name: string;
  submitter_rules: null;
  fields: Field[];
  steps: Step[];
  start_step_id: string;
  modifier_user: number;
  start_at: string;
  end_at: string;
  created_at: string;
  updated_at: string;
}

export interface FormField {
  name: string;
  type: string;
  label: string;
  default_value: string;
  is_required: boolean;
  extra: any;
}

export interface FormSection {
  name: string;
  fields: FormField[];
}

export interface FormPage {
  name: string;
  page_number: number;
  sections: FormSection[];
}

export interface FormApproval {
  id: string;
  name: string;
  pages: FormPage[];
  // modifier_user: number;
  workspace_slug: string;
  external_form_id: string | null;
  external_form_app: string | null;
  created_at: string;
  updated_at: string;
}

export interface SubmitInfo {
  approval_id: string;
  approval_name: string;
  step_id: string;
  step_name: string;
  status: string;
  step_description: string;
  // submit_fields: Submitfield[];
  form:FormApproval;
  action_buttons: null;
  is_final_step: boolean;
}

// export interface SubmitFieldInfo {
//   approval_id: string;
//   step_id: string;
//   step_name: string;
//   status: string;
//   step_description: string;
//   submit_fields: Submitfield[];
//   action_buttons: ActionButton[];
// }

// interface Submitfield {
//   name: string;
//   display_name: string;
//   type: string;
//   default_value: string;
//   placeholder: string;
//   options: null;
//   is_required: boolean;
//   is_editable: boolean;
// }

interface Step {
  pre_actions: null;
  post_actions: null;
  nexts: (Next | Nexts2)[];
  step_id: string;
  name: string;
  description: string;
  status: string;
  field_permissions: FieldPermission[];
  action_buttons: ActionButton[] | null;
  approval_type: string;
  approvers: any[];
  approve_require: string;
  ccs: any[];
}

interface ActionButton {
  display_name: string;
  value: string;
}

interface FieldPermission {
  field_name: string;
  is_required: boolean;
  is_visible: boolean;
  is_editable: boolean;
}

interface Nexts2 {
  condition_groups: ConditionGroup[] | null;
  step_id: string;
}

interface ConditionGroup {
  conditions: Condition[];
}

interface Condition {
  field: string;
  operator: string;
  value: string;
  value_field: string;
}

interface Next {
  condition_groups: null;
  step_id: string;
}

export interface Field {
  name: string;
  display_name: string;
  type: string;
  default_value: string;
  placeholder: string;
  options: null;
  reference_update: string;
}
