

from fractions import Fraction
from itertools import chain, combinations
from math import comb


def get_input_set(prompt):
    """Helper function to get a set from user input."""
    raw_input = input(prompt)
    elements = raw_input.split()
    return set(elements)


def power_set(s):
    """Generate the power set of a given set s."""
    return list(chain.from_iterable(combinations(s, r) for r in range(len(s) + 1)))


def get_subset(power_set):
    """Helper function to get a subset of the power set from user input."""
    # print("Power set:", power_set)
    subset = []
    n = 1
    while True:
        element = input(
            f"The elements of e_{n} : (Press enter to terminate): "
        )
        if element == "":
            break
        subset.append(tuple(element.split()))
        n += 1
    return subset


def delta_function(e_name, E_named):
    # Take the considered set and the elements
    e_set = E_named[e_name]  # All elements in all sets
    not_in_e_set = U - e_set  # the elements not in p_set
    results = {}
    # For every elements not in p_set
    for element in not_in_e_set:
        total_sum = 0
        # counter set to zero for every duo at the start
        for other_element in e_set:  # creates duo's with the other elements in p_set
            for other_e_set in E_named.values():
                # Check if this pair is present in at least one of the other sets
                if {element, other_element}.issubset(other_e_set):
                    # If the duo is in any other set, increment the counter
                    total_sum += 1
                    continue  # Exit loop after counter is incremented
        # Save the value found for each element
        results[element] = total_sum
    return results


def create_membership_matrix(E_keys, e_name):
    membership_matrix = {e_key: {} for e_key in E_keys}

    for e_key in E_keys:
        delta_results = delta_function(e_key, e_name)
        g_coeff = len(e_name[e_key]) * (len(E_named) - 1)
        for element in U:
            if element in delta_results:
                membership_value = Fraction(delta_results[element], g_coeff)
            else:
                membership_value = 1  # If there is no gamma result, assign 1
            membership_matrix[e_key][element] = membership_value

    return membership_matrix


def print_matrix(matrix):
    """Print the membership matrix in a well-formatted table."""
    elements = sorted(next(iter(matrix.values())).keys())  # U elements

    # Print header with column spacing
    print(f"{'':>5}", end="")
    for element in elements:
        print(f"{element:>10}", end="")
    print("\n" + "-" * (5 + 10 * len(elements)))  # Add separator line

    # Print each row with values
    for e_key, values in matrix.items():
        print(f"{e_key:>5}", end="")  # Row labels (e_1, e_2, ...)
        for element in elements:
            value = values[element]
            # Convert Fraction to float for display
            if isinstance(value, Fraction):
                value = float(value)
            print(f"{value:>10.2f}", end="")
        print()

    # Print column sums at the bottom
    print("-" * (5 + 10 * len(elements)))  # Add separator line
    print(f"{'Sum':>5}", end="")
    for element in elements:
        column_sum = sum(float(row[element]) for row in matrix.values())
        print(f"{column_sum:>10.2f}", end="")
    print()


# Get the set U from the user
U = get_input_set("Enter the elements of set U (separate with spaces): ")

# Generate the power set of U
P_power_set = power_set(U)

# Get the subset P from the power set
E_named = get_subset(P_power_set)

# Convert list of tuples to list of sets for better readability
E = [set(subset) for subset in E_named]

# Assign names e_1, e_2, ... to elements in E
e_name = {f"e_{i+1}": subset for i, subset in enumerate(E)}

# Calculate membership matrix
membership_matrix = create_membership_matrix(e_name.keys(), e_name)


E_keys = e_name.keys()
# Print the resulting matrix
print("============RESULTS================")

for e_key in E_keys:
    delta_results = delta_function(e_key, e_name)
    g_coeff = len(e_name[e_key]) * (len(E_named) - 1)
    print(f"Proper coefficient for {e_key}:", g_coeff)
    # i = 1
    for u, delta_sum in delta_results.items():
        M = Fraction(delta_sum, g_coeff)
        print(
            f"The relative membership value for the element {u} that is not a member of {e_key} is {M}.")
        # i += 1

print_matrix(membership_matrix)


# Get the value at row y, column x in the matrix
# def get_from_position(y, x, matrix):
#     return list(matrix.values())[y - 1][f"{x}"]


# Get the sum of a column in the matrix
def get_sum_of_column(column_element, matrix):
    total = 0
    for row in matrix.values():
        if column_element in row:
            total += float(row[column_element])
    return round(total, 2)


# Create a dictionary with column sums
def create_sum_dictionary_of_columns(matrix):
    elements = sorted(next(iter(matrix.values())).keys())  # U elements
    return {
        f"s({element})": get_sum_of_column(element, matrix)
        for element in elements
    }


# Get the names of columns with maximum sum
def get_elements_with_max_columns(matrix):
    column_sums = create_sum_dictionary_of_columns(matrix)
    max_sum = max(column_sums.values())
    return [
        element
        for element, sum_value in column_sums.items()
        if sum_value == max_sum
    ]


print("============DECISION MAKING PHASE================")
print(
    "Column sums for each element: -->",
    create_sum_dictionary_of_columns(membership_matrix),
)
print(
    "The best choice according to the given criteria (highest column score): -->",
    get_elements_with_max_columns(membership_matrix),
)
