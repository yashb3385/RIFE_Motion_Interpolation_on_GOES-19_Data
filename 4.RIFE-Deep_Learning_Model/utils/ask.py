def ask_y_n(ques):
    while True:
        ans = input(ques).strip().lower()
        if ans in ['y', 'n']:
            break 
        print("\nInvalid input! Please enter exactly 'y' or 'n'.\n")
    return ans
