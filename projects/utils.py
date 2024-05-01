def filter_by_budget(queryset, budget_filter):
    try:
        if 'bgt' in budget_filter:
            budget_greater_than = int(budget_filter['bgt'])
            queryset = queryset.filter(budget_needed__gte=budget_greater_than)

        if 'blt' in budget_filter:
            budget_less_than = int(budget_filter['blt'])
            queryset = queryset.filter(budget_needed__lte=budget_less_than)
    except ValueError as ve:
        raise ValueError("Invalid budget filter parameter: {}".format(ve))

    return queryset


def filter_projects(queryset, data, request):
    allowed_budget_keys = ['bgt', 'blt']
    budget_filter = {key: data.pop(key, None) for key in allowed_budget_keys if key in data}

    not_exact_key = 'project_name'
    if not_exact_key in data:
        project_name_filter = data.pop('project_name')
        queryset = queryset.filter(project_name__icontains=project_name_filter)

    queryset = queryset.filter(**data)

    if request.user.is_authenticated and request.user.is_investor and budget_filter:
        queryset = filter_by_budget(queryset, budget_filter)

    return queryset
