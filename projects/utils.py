from django.db.models import Sum
from projects.models import Investment


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


def compare_industries(industry1, industry2):
    difference = {}
    if industry1 != industry2:
        difference = {
            "project1": industry1.name if industry1 else None,
            "project2": industry2.name if industry2 else None
        }
    return difference


def calculate_difference(project1, project2):
    difference = {}
    for field in project1._meta.fields:
        field_name = field.name
        if getattr(project1, field_name) != getattr(project2, field_name):
            if field_name == "industry":
                industry_difference = compare_industries(project1.industry, project2.industry)
                difference[field_name] = industry_difference
            else:
                difference[field_name] = {
                    "project1": getattr(project1, field_name),
                    "project2": getattr(project2, field_name)
                }
    return difference


def calculate_investment(investor, project, investment_amount):
    """
    The calculate_investment function takes in an investor, a project and the amount to be invested.
    It then updates the investment_amount of the investor by subtracting it from his/her current investment_amount.
    The budget_ready of the project is updated by adding it to its current budget_ready value.
    An Investment object is created with details about who invested what into which project and how much was invested.
    If after this transaction, if budget ready exceeds or equals budget needed for that particular project, then status of that particular
    project changes to 'completed'. The function returns a dictionary containing information for Response.

    :param investor: Get the investor object from the database
    :param project: Get the project object from the database
    :param investment_amount: Pass the amount of money that the investor wants to invest in a project
    :return: A dictionary for Response.

    """
    investor.investment_amount -= investment_amount
    investor.save()

    project.budget_ready += investment_amount
    project.save()

    investment = Investment(
        investor=investor,
        project=project,
        amount_invested=investment_amount,
    )
    investment.save()

    if project.budget_ready > project.budget_needed:
        project.status = 'completed'
        project.save()
    investor_investment = Investment.objects.filter(investor=investor, project=project)
    investor_investment = investor_investment.aggregate(total_investment=Sum('amount_invested'))
    total_investment_amount = investor_investment['total_investment'] if investor_investment[
                                                                             'total_investment'] is not None else 0
    return {
        "investor_name": investor.user.first_name,
        "project_name": project.project_name,
        "invested": investment_amount,
        "total_investment_by_investor_to_project": total_investment_amount,
        "project_budget_needed": project.budget_needed,
        "project_budget_ready": project.budget_ready,
        "project_status": project.status
    }
