import os

def get_summary_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Look for triple-quoted docstring
    in_docstring = False
    docstring = []
    for line in lines:
        if line.strip().startswith('"""') or line.strip().startswith("'''"):
            if in_docstring:
                docstring.append(line.strip().strip('"""').strip("'''"))
                break
            else:
                in_docstring = True
                docstring.append(line.strip().strip('"""').strip("'''"))
        elif in_docstring:
            docstring.append(line.strip())

    if docstring:
        return ' '.join(docstring).strip()

    # Fallback to first comment line
    for line in lines:
        if line.strip().startswith('#'):
            return line.strip('#').strip()

    return "No description available"

def describe_project(root):
    print(f"Project structure summary for '{root}':\n")
    for dirpath, _, filenames in os.walk(root):
        indent = '    ' * (dirpath.count(os.sep) - root.count(os.sep))
        print(f"{indent}{os.path.basename(dirpath)}/")
        for filename in sorted(filenames):
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                description = get_summary_from_file(filepath)
                print(f"{indent}    {filename} — {description}")

describe_project('ecg_processor')
