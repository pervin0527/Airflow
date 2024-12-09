import random

class AdvancedHeaderGenerator:
    def __init__(self):
        self.base_user_agents = [
            {"os": "Windows", "agent": "Mozilla/5.0 (Windows NT {version}; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36", "versions": ["10.0", "8.1", "7"], "chrome_versions": ["90.0.4430.212", "91.0.4472.124", "92.0.4515.159"]},
            {"os": "Mac", "agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X {version}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15", "versions": ["10_15_7", "11_2_3", "10_14_6"], "chrome_versions": []},
            # {"os": "iPhone", "agent": "Mozilla/5.0 (iPhone; CPU iPhone OS {version} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1", "versions": ["14_0", "13_4", "12_3"], "chrome_versions": []},
            # {"os": "Android", "agent": "Mozilla/5.0 (Linux; Android {version}; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Mobile Safari/537.36", "versions": ["10", "9", "8"], "chrome_versions": ["90.0.4430.210", "91.0.4472.120", "92.0.4515.158"]},
            # {"os": "iPad", "agent": "Mozilla/5.0 (iPad; CPU OS {version} like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1", "versions": ["14_0", "13_6", "12_4"], "chrome_versions": []}
        ]
        self.accept_languages = ["ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7", "ko-KR,ko;q=0.8,en-US;q=0.6,en;q=0.4"]
        self.accept_encodings = ["gzip, deflate, br", "gzip, deflate"]
        self.content_types = ["application/json", "text/html; charset=UTF-8"]
        self.accepts = ["text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8", "application/json, text/plain, */*"]
        self.connections = ["keep-alive"]
        
        
    def generate_user_agent(self):
        base = random.choice(self.base_user_agents)
        version = random.choice(base["versions"])
        if base["os"] in ["Windows", "Android"] and base["chrome_versions"]:
            chrome_version = random.choice(base["chrome_versions"])
            return base["agent"].format(version=version, chrome_version=chrome_version)
        else:
            return base["agent"].format(version=version)
        
        
    def generate_headers(self):
        headers = {
            "User-Agent": self.generate_user_agent(),
            "Content-Type": random.choice(self.content_types),
            "Accept": random.choice(self.accepts),
            "Accept-Language": random.choice(self.accept_languages),
            "Connection": random.choice(self.connections),
            "Accept-Encoding": random.choice(self.accept_encodings),
        }
        return headers