# algorithms.py

def insertion_sort_by_key(items: list[dict], key: str) -> list[dict]:

    arr = items.copy()

    for i in range(1, len(arr)):

        current = arr[i]

        j = i - 1

        while j >= 0 and arr[j][key] < current[key]:

            arr[j + 1] = arr[j]

            j -= 1

        arr[j + 1] = current

    return arr


def binary_search_iterative(
    sorted_titles: list[str],
    target: str
) -> int:

    start = 0
    end = len(sorted_titles) - 1

    while start <= end:

        mid = start + (end - start) // 2

        if sorted_titles[mid] == target:
            return mid

        elif sorted_titles[mid] < target:
            start = mid + 1

        else:
            end = mid - 1

    return -1


def binary_search_recursive(
    sorted_titles: list[str],
    target: str,
    start: int,
    end: int
) -> int:

    if start > end:
        return -1

    mid = start + (end - start) // 2

    if sorted_titles[mid] == target:
        return mid

    if sorted_titles[mid] < target:
        return binary_search_recursive(
            sorted_titles,
            target,
            mid + 1,
            end
        )

    return binary_search_recursive(
        sorted_titles,
        target,
        start,
        mid - 1
    )


def linear_search(
    items: list[dict],
    key: str,
    value
):

    found = False

    result = None

    for item in items:

        if str(item[key]).strip().lower() == str(value).strip().lower():

            found = True

            result = item

            break

    if found:
        return result

    return None