from polar.kit.schemas import Schema


class OAuthAccessToken(Schema):
    access_token: str
    expires_in: int
    expires_at: int
    refresh_token: str
    refresh_token_expires_in: int


class GitHubIssue(Schema):
    raw: str
    owner: str | None = None
    repo: str | None = None
    number: int

    @property
    def canonical(self) -> str:
        if self.owner and self.repo:
            return f"{self.owner.lower()}/{self.repo.lower()}#{self.number}"
        else:
            return f"#{self.number}"


class GithubUser(Schema):
    username: str
    avatar_url: str
