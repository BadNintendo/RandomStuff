memo = {}

def is_satisfied(clause, assignment):
    return any((lit > 0 and assignment.get(abs(lit), False)) or (lit < 0 and not assignment.get(abs(lit), False)) for lit in clause)

def is_unsatisfied(clause, assignment):
    return all((lit > 0 and not assignment.get(abs(lit), True)) or (lit < 0 and assignment.get(abs(lit), False)) for lit in clause)

def dpll(clauses, assignment={}):
    key = tuple(sorted(assignment.items()))
    if key in memo:
        return memo[key]

    if all(is_satisfied(clause, assignment) for clause in clauses):
        memo[key] = assignment
        return assignment

    if any(is_unsatisfied(clause, assignment) for clause in clauses):
        memo[key] = None
        return None

    # Pure literal elimination
    all_literals = {lit for clause in clauses for lit in clause}
    pure_literals = {lit for lit in all_literals if -lit not in all_literals}
    for lit in pure_literals:
        assignment[abs(lit)] = lit > 0

    # Unit propagation
    unit_clauses = [clause for clause in clauses if len(clause) == 1]
    for unit in unit_clauses:
        if len(unit) == 0:
            continue  # Skip empty clauses to avoid IndexError
        lit = unit[0]
        assignment[abs(lit)] = lit > 0
        clauses = [clause for clause in clauses if lit not in clause]
        for clause in clauses:
            if -lit in clause:
                clause.remove(-lit)

    # Select unassigned variable and try both True and False
    unassigned_vars = {abs(lit) for clause in clauses for lit in clause if abs(lit) not in assignment}
    if not unassigned_vars:
        return None

    variable = unassigned_vars.pop()
    for value in [True, False]:
        local_assignment = assignment.copy()
        local_assignment[variable] = value
        result = dpll(clauses, local_assignment)
        if result is not None:
            memo[key] = result
            return result

    memo[key] = None
    return None

def main():
    test_cases = [
        ([[1, -2], [2, 3], [-1, -3]], True),
        ([[1], [-1]], False),
        ([[1, 2, 3], [-1, -2], [2, -3], [-2, 3]], True)
    ]

    for i, (clauses, expected) in enumerate(test_cases):
        memo.clear()  # Clear memoization before each test
        result = dpll(clauses) is not None
        print(f"Test {i + 1}: {'Pass' if result == expected else 'Fail'}")

if __name__ == "__main__":
    main()
