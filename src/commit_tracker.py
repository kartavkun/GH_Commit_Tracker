# src/commit_tracker.py
import os
import time
import subprocess
import re
import requests
from dotenv import load_dotenv

load_dotenv()

class CommitTracker:
    def __init__(self, repo_url, check_interval=10, bot_token=None, chat_id=None):
        self.repo_url = repo_url
        self.check_interval = check_interval
        self.repo_path = self.get_repo_path_from_url()
        self.last_commit = None
        self.bot_token = bot_token
        self.chat_id = chat_id

    def get_repo_path_from_url(self):
        match = re.search(r'github\.com/(.*?)/(.*?)(\.git)?$', self.repo_url)
        if match:
            return os.path.join(os.getcwd(), f"{match.group(1)}_{match.group(2)}")
        return None

    def clone_or_pull_repo(self):
        if os.path.exists(self.repo_path):
            subprocess.call(['git', '-C', self.repo_path, 'pull'])
        else:
            subprocess.call(['git', 'clone', self.repo_url, self.repo_path])

    def get_latest_commit(self):
        try:
            commit_hash = subprocess.check_output(
                ['git', '-C', self.repo_path, 'rev-parse', 'HEAD']
            ).strip().decode('utf-8')
            commit_message = subprocess.check_output(
                ['git', '-C', self.repo_path, 'log', '--format=%s', '-n', '1']
            ).strip().decode('utf-8')
            commit_description = subprocess.check_output(
                ['git', '-C', self.repo_path, 'log', '--format=%b', '-n', '1']
            ).strip().decode('utf-8') or "Пусто :("
            commit_time = subprocess.check_output(
                ['git', '-C', self.repo_path, 'log', '--format=%cd', '-n', '1']
            ).strip().decode('utf-8')

            return commit_hash, commit_message, commit_description, commit_time
        except subprocess.CalledProcessError:
            return None, None, None, None

    def send_message_to_telegram(self, message):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        params = {'chat_id': self.chat_id, 'text': message}
        response = requests.get(url, params=params)
        return response

    def track_commits(self):
        if not self.repo_path:
            print("[ERROR] Invalid repository URL")
            return

        self.clone_or_pull_repo()
        self.last_commit, _, _, _ = self.get_latest_commit()
        print(f"[INFO] Tracking repository: {self.repo_url}")
        print(f"[INFO] Initial commit: {self.last_commit}")

        while True:
            time.sleep(self.check_interval)
            self.clone_or_pull_repo()
            latest_commit, commit_message, commit_description, commit_time = self.get_latest_commit()
            if latest_commit and latest_commit != self.last_commit:
                commit_url = f"{self.repo_url}/commit/{latest_commit}"
                message = f"""
🎉 Новый коммит!

📝 Сообщение коммита: {commit_message}
📜 Описание коммита: {commit_description}
⏰ Время коммита: {commit_time}
🔗 Ссылка: {commit_url}
                """
                print(f"[NEW COMMIT] {commit_url}")
                self.send_message_to_telegram(message)
                self.last_commit = latest_commit
