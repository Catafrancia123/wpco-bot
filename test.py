from saveloader import load

user = "catamapp"
to_user = "dean1p"

print(f"{to_user}'s total points: {load('save.json', f'{to_user}_pts', 'points')}\nAdded by {user}")

