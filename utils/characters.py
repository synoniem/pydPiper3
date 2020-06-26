print('')
print("   ", end=' ')
for i in range(0,16):
    print("{:3d}  ".format(i), end=' ')
print('')

for i in range(0,16):
    print("{:3d}  ".format(i*16), end=' ')
    for j in range(0,16):
        if (j*16)+i > 32:
            print("{0}    ".format(chr((j*16)+i).encode('utf-8')), end=' ')
        else:
            print("     ", end=' ')
    print('')
