import Performance
import time

PRINT_COUNT = 100000
text_length = 0

@Performance.inspect
def generate_text(x: int) -> str:
    return f"Performance control: {int(time.perf_counter())} ({int(x*100/PRINT_COUNT)}%)"

@Performance.inspect
def add_length(t: str) -> None:
    global text_length
    text_length = len(t)

@Performance.inspect
def print_time(x: int) -> None:
    text = generate_text(x)
    print(text,end="\r")
    add_length(text)

for i in range(PRINT_COUNT):
    print_time(i)

print(" "*text_length, end="\r")
Performance.print_total_log()
print()
Performance.print_overview_log()