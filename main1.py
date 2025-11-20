import Performance

# y = 0.2x**2

@Performance.inspect
def print_solution(text: str) -> None:
    print(text)

@Performance.inspect
def generate_output(area: float) -> None:
    return f"Total area: {area}"

@Performance.inspect
def area(x: float) -> float:
    y = 0.2*x**2
    return x*y

@Performance.inspect
def calculate(count: int) -> float:
    total = 0.0
    for x in range(1, count+1):
        total += area(x)
    return total

@Performance.inspect
def solve(count: int) -> None:
    a = calculate(count)
    t = generate_output(a)
    print_solution(t)

solve(6)

print()
Performance.print_total_log()
print()
Performance.print_overview_log()