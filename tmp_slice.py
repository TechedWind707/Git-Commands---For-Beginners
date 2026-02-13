# from pathlib import Path
# import sys

# path = Path(sys.argv[1])
# lines = path.read_text(encoding="utf-8").splitlines()
# if len(sys.argv) == 2:
#     print(len(lines))
#     raise SystemExit(0)

# start = int(sys.argv[2])
# end = int(sys.argv[3])
# for i in range(start - 1, min(end, len(lines))):
#     print(lines[i])
