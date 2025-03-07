import { USER_KEY, USER_PERMISSION } from '@/api-requests';
import { resources } from '@/contexts/resources';
import { IPermission } from '@/interfaces';
import { CanParams, CanReturnType, IAccessControlContext } from '@refinedev/core';

export const accessControlProvider: Required<IAccessControlContext> = {
  can: async ({ resource, action, params }: CanParams): Promise<CanReturnType> => {
    return { can: true }; // remove this line to enable access control
    const permissions = JSON.parse(localStorage.getItem(USER_PERMISSION) || '');
    const userInformation = JSON.parse(localStorage.getItem(USER_KEY) || '');
    const all_resources = resources;

    // add parent menu to each permission
    // because we need to enable can for parent menu
    // in order to view sub menu

    if (userInformation.user_status == 107) {
      if (resource === 'super admin') {
        return { can: true };
      }
      if (
        all_resources.some(
          resourceData => resourceData.meta.parent?.toLowerCase() === 'super admin' && resourceData.name === resource
        )
      ) {
        return { can: true };
      }
      return { can: true };
    } else {
      if (resource === 'super admin') {
        return { can: false };
      }
    }

    if (permissions === null) {
      return { can: false, reason: 'Unauthorized' };
    }
    const permissions_with_parent = permissions
      .filter((permission: IPermission) => {
        const matchingName = all_resources.find(resource => permission.resource === resource.name);
        return matchingName;
      })
      .map((permission: IPermission) => ({
        ...permission,
        parent: all_resources.find(resource => permission.resource === resource.name)?.meta.parent?.toLowerCase()
      }));

    if (resource === undefined) {
      // set can->true to default page (/ path)
      return { can: true };
    } else if (
      permissions_with_parent.some(
        (permission: IPermission) => permission.resource === resource && permission.action === action
      )
    ) {
      // set can->true for each each sub-menu and action
      return { can: true };
    } else if (
      permissions_with_parent.some((permission: IPermission) => permission.parent === resource && action === 'list')
    ) {
      // set can->true for parent menu
      return { can: true };
    }

    return { can: false, reason: 'Unauthorized' };
  },
  options: {
    buttons: {
      hideIfUnauthorized: false // hide button or show button but can not click
    }
  }
};
