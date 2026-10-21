ACADEMY_COURSES = {
    "frontend": "Frontend Engineering",
    "backend": "Backend Engineering",
    "cybersecurity": "Cyber Security",
    "data_analysis": "Data Analysis",
    "product_design": "Product Design",
}

SIWES_COURSES = {
    **ACADEMY_COURSES,
    "other": "Other",
}

ACADEMY_PRICE = 100000
SIWES_PRICE = 50000


def get_price(student_type):
    if student_type == "academy":
        return ACADEMY_PRICE
    if student_type == "siwes":
        return SIWES_PRICE
    raise ValueError("Unknown student type.")
