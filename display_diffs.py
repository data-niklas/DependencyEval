import sys
import json
import subprocess
import os

def main():
    dataset = sys.argv[1]
    diff_dir = sys.argv[2]
    if not os.path.exists(diff_dir):
        os.makedirs(diff_dir)
    with open(dataset, "r") as f:
        items = [json.loads(i) for i in f.read().splitlines()]
    for item in items:
        code = "\n".join(item["import_statements"]) + "\n\n"
        if item["context"] != "":
            code += item["context"] + "\n\n"
        code += item["function_signature"] + "\n  " + item["function_documentation"] + "\n" + item["solution"]

        code2 = item["generated_code"]
        with open("__solution__.py", "w") as f:
            f.write(code)
        with open("__generated__.py", "w") as f:
            f.write(code2)
        try:
            diff = subprocess.run(["diff", "--text", "--unified", "--new-file", "__solution__.py", "__generated__.py"], stderr=subprocess.STDOUT, stdout=subprocess.PIPE).stdout.decode()
            with open(os.path.join(diff_dir, item["task_name"] + ".diff"), "w") as f:
                f.write(diff)
        except BaseException as e:
            print(e)
            print("Ran into an error while diffing")
        os.remove("__solution__.py")
        os.remove("__generated__.py")

        

if __name__ == "__main__":
    main()