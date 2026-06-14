# x = [i**2 for i in range(1000000000)]


# for el in x:
#     print(el)


def gen(n):
    for i in range(n):
        yield i**2  # pause the function here


g = gen(10)

for i in g:
    print(i)

print("---")

b = gen(10)
print(next(b))
print(next(b))
print(next(b))
print(next(b))

print("---")


def agen(n):
    # kind of pause each time, store internal state, and by next call it continue from next one
    yield 1
    yield 10
    yield 100
    yield 1000


b = agen(10)
print(next(b))

print(next(b))
print(next(b))
print(next(b))
# print(next(b)) # will raise the error StopIteration (bc there is no more values to yield)


def bgen(n):
    for i in range(n):
        yield i**2


x = [i**2 for i in range(10000)]

g = bgen(1000)
import sys

print("----")

print(sys.getsizeof(x))
print(sys.getsizeof(g))
