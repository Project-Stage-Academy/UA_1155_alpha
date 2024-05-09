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


def calculate_difference(project1, project2):
    """
    Calculate the difference between two projects.
    This function compares each field of two project instances and returns the difference.
    Parameters:
    - project1 (Project): The first project instance.
    - project2 (Project): The second project instance.
    Returns:
    dict: A dictionary containing the difference between the two projects.
    """
    difference = {}
    for field in project1._meta.fields:
        field_name = field.name
        if getattr(project1, field_name) != getattr(project2, field_name):
            # Check if the field is 'industry' and handle it differently
            if field_name == 'industry':
                industry_difference = compare_industries(project1.industry, project2.industry)
                difference[field_name] = industry_difference
            else:
                difference[field_name] = {
                    'project1': getattr(project1, field_name),
                    'project2': getattr(project2, field_name)
                }
    return difference


def compare_industries(industry1, industry2):
    """
    Compare two industry instances and return their difference.
    Parameters:
    - industry1 (Industry): The first industry instance.
    - industry2 (Industry): The second industry instance.
    Returns:
    dict: A dictionary containing the difference between the two industries.
    """
    difference = {}
    if industry1 != industry2:
        difference = {
            'project1': industry1.name if industry1 else None,
            'project2': industry2.name if industry2 else None
        }
    return difference
