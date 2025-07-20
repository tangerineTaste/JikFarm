class Member:
    def __init__(self, member_id, login_id, nickname, name, password, is_admin, created_at, updated_at):
        self.member_id = member_id
        self.login_id = login_id
        self.nickname = nickname
        self.name = name
        self.password = password
        self.is_admin = is_admin
        self.created_at = created_at
        self.updated_at = updated_at
        