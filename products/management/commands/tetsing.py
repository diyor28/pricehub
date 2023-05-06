def compute_avg(func):
    def wrapper():
        pass
    return wrapper


@compute_avg
def get_students():
    return [
        {
            "name": "ibragim",
            "marks": [8, 0],
        },
        {
            "name": "sheikh",
            "marks": [8, 0, 1],
        },
        {
            "name": "ozod",
            "marks": [8, 0, 3, 4],
        },

    ]
print(get_students)