
def variance(numbers)-> float:
    total = 0
    mean = 0

    for n in numbers:
        mean += n / len(numbers)

    for n in numbers:
        total += (n - mean) ** 2

    return total / len(numbers)


def avg(numbers) -> float:
  total = 0
  for n in numbers:
   total += n/len(numbers)

  return total

def min(numbers) -> float:
    smallest = numbers[0]
    for n in numbers[1:]:
        if n < smallest:
            smallest = n
    return smallest
  

def max(numbers) -> float:
    largest = numbers[0]
    for n in numbers[1:]:
        if n > largest:
            largest = n
    return largest