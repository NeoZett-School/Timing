import wrapper
import time

@wrapper.threaded
def add(a: int, b: int) -> int: 
    return a + b

res = wrapper.new_thread_resolve(add)
res.start_recording()
add(5, 10)
res.wait()
print(res.value)
wrapper.cleanup()