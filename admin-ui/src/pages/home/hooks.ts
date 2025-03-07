
export const useFilteredResources = (resources: any[], filter: string) => {
  return resources.filter(
    (resource) => resource.list && resource.meta.label.toLowerCase().includes(filter.toLowerCase())
  );
};
