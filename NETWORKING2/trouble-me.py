import subprocess

print('========== TROUBLE ME 1.0 ==========')
print('Testing IP:')

res = subprocess.run(['ip', '-br', 'link'], capture_output=True, text=True, check=True)
ip = res.stdout.splitlines()

for i in ip:
    x = i.split()
    if x[1] == "UP":
        print(x[0] + "..........", "PASSED")
    elif x[1] == "UNKNOWN":
        print(x[0] + "..........", "WARNING")
    else:
        print(x[0] + "..........", "FAIL")

