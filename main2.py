import wrapper

@wrapper.threaded
def add(a: int, b: int) -> int: 
    return a + b

res = add(5, 10)
print(res.result())