import time

# Goal modify the behavior of the function without touching the function itself


# Another example


def func(f):
    def wrapper():
        print("started")
        f()
        print("ended")

    return wrapper


def bfunc(f):
    def wrapper(*args, **kwargs):
        print("started")
        f(*args, **kwargs)
        print("ended")

    return wrapper


@bfunc
def bfunc2(x, y):
    print(x)
    return y


def func2():
    print("i am in func2")


@func
def func3():
    print("I am in func3")


# Method1
test_a = func(func2)
test_a()
print("---------------")

# Method2
func3()
print("---------------")

bfunc2(5, 10)


def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Execution time for {func.__name__}: {end_time - start_time} seconds")
        return result

    return wrapper


# Method 1:
# @timer
# def example_function(n):
#     return f'The sum is {sum(range(n))}'


# Method 2:
def example_function(n):
    return f"The sum is {sum(range(n))}"


example_function = timer(example_function)


# Test
print(example_function(1000000))

print("---------------")


@timer
def test():
    for _ in range(1000000):
        pass


@timer
def test2():
    time.sleep(2)


test()
test2()
