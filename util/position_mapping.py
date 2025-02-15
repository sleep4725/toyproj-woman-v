def position_re_value_return(position: str)-> str:
    if position == "MB":
        return "MIDDLE BLOCKER"
    elif position == "S":
        return "SETTER"
    elif position == "OP":
        return "OPPOSITE"
    elif position == "OH":
        return "OUTSIDE HITTER"
    elif position == "L":
        return "LIBERO"
    else:
        return "ERROR"