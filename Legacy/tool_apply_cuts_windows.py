import os
import sys
import subprocess
import glob

# Windows CapCut path
PROJECTS_ROOT = os.path.join(
    os.environ['LOCALAPPDATA'],
    'JianyingPro', 'User Data', 'Projects', 'com.lveditor.draft'
)

def find_latest_project():
    if not os.path.exists(PROJECTS_ROOT):
        print(f"CapCut projects folder not found at: {PROJECTS_ROOT}")
        print("Please make sure CapCut is installed and you have created at least one project.")
        return None
        
    subdirs = glob.glob(os.path.join(PROJECTS_ROOT, '*'))
    valid_projects = []
    for d in subdirs:
        if os.path.isdir(d) and os.path.exists(os.path.join(d, 'draft_info.json')):
            valid_projects.append(d)
            
    if not valid_projects:
        return None
    return max(valid_projects, key=os.path.getmtime)

def main():
    print("---------------------------------------")
    print("Finding your latest CapCut project...")
    latest_proj = find_latest_project()
    
    if not latest_proj:
        print("No CapCut projects found!")
        print("Please OPEN CapCut, create a project, import video, and CLOSE it.")
        input("Press Enter to exit...")
        return

    latest_json = os.path.join(latest_proj, 'draft_info.json')
    print(f"Target: {os.path.basename(latest_proj)}")
    print("---------------------------------------")
    
    # Read existing cuts.txt
    cuts_file = 'cuts.txt'
    with open(cuts_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # Rewrite cuts.txt with NEW path
    new_lines = []
    new_lines.append(f"PATH: {latest_json}\n")
    
    for line in lines:
        if line.strip().startswith('PATH:'):
            continue
        new_lines.append(line)
        
    with open(cuts_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
        
    print("Running automation...")
    subprocess.run(['python', 'automate_cuts.py'])
    input("Press Enter to close...")

if __name__ == "__main__":
    main()
