import moviepy, os
p = os.path.dirname(moviepy.__file__)
print('moviepy package path:', p)
for fn in sorted(os.listdir(p)):
    print(fn)
