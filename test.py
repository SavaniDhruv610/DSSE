import os
import subprocess
from pydriller import Repository
import re

def analyze_repo():
    repo_url = "https://github.com/apache/jclouds.git"
    local_dir = "jclouds_local"
    issues = ["JCLOUDS-27", "JCLOUDS-43", "JCLOUDS-276", "JCLOUDS-435", "JCLOUDS-1548"]

    # 1. Clone locally if not exists
    if not os.path.exists(local_dir):
        print(f"Cloning {repo_url} into local directory '{local_dir}'...")
        subprocess.run(["git", "clone", repo_url, local_dir], check=True)
    else:
        print(f"Local directory '{local_dir}' already exists. Analyzing local repository...")

    total_commits = 0
    all_unique_files = set()
    total_dmm_score = 0.0

    # Create a regex to find any of the JIRA issues in the commit message
    issue_pattern = re.compile(r'\b(?:' + '|'.join(issues) + r')\b', re.IGNORECASE)

    print("Analyzing commits... (This may take a few minutes)")

    # Traverse commits in the local repository
    for commit in Repository(local_dir).traverse_commits():
        if issue_pattern.search(commit.msg):
            total_commits += 1
            
            for mod in commit.modified_files:
                # 1. Track Additions, Modifications, and Deletions
                if mod.change_type.name in ['ADD', 'MODIFY', 'DELETE']:
                    path = mod.new_path if mod.new_path else mod.old_path
                    if path:
                        all_unique_files.add(path)
                
            # 2. Use Pydriller's native DMM Metrics
            dmm_size = commit.dmm_unit_size
            dmm_complexity = commit.dmm_unit_complexity
            dmm_interfacing = commit.dmm_unit_interfacing
            
            # Properties are None if Pydriller could not calculate DMM for the commit
            if dmm_size is not None and dmm_complexity is not None and dmm_interfacing is not None:
                # Average the three DMM properties
                commit_dmm_score = (dmm_size + dmm_complexity + dmm_interfacing) / 3.0
                total_dmm_score += commit_dmm_score

    # 3. Output the final statistics
    if total_commits > 0:
        # 1. Average unique files changed across all found commits
        avg_files = len(all_unique_files) / total_commits
        # 2. Average DMM score across all found commits
        avg_dmm = total_dmm_score / total_commits
        
        print(f"total commits analyzed: {total_commits}")
        print(f"average number of files changed: {avg_files:.2f}")
        print(f"average DMM matrics: {avg_dmm:.2f}")
    else:
        print("\nNo commits found for the specified JIRA issues.")

if __name__ == "__main__":
    analyze_repo()