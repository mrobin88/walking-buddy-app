def twoSum(nums, target):
    index_map = {}  # Stores number -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in index_map:
            return [index_map[complement], i]
        index_map[num] = i
    return None  # No solution found

def main():
    nums = [2, 7, 11, 15]
    target = 9
    result = twoSum(nums, target)
    
    if result is not None:
        i, j = result
        print(f"Indices: {result}")
        print(f"Values: {nums[i]} + {nums[j]} = {target}")
    else:
        print("No two numbers add up to the target")

if __name__ == "__main__":
    main()
