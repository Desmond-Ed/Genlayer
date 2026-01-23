# v0.1.0
# { "Depends": "py-genlayer:latest" }

from genlayer import *
import json


class SocialProofLibrary(gl.Contract):

    verified_users: TreeMap[gl.Address, str]
    supported_platforms: DynArray[str]
    whitelisted_domains: DynArray[str]

    def __init__(self):
        self.supported_platforms = ["github", "twitter", "linkedin"]
        self.whitelisted_domains = ["github.com", "twitter.com", "linkedin.com"]
        self.verified_users = {}

    # --- internal helpers ---

    def _is_domain_whitelisted(self, url: str) -> bool:
        for domain in self.whitelisted_domains:
            if domain in url:
                return True
        return False

    # --- core verification ---

    @gl.public.write
    async def verify_user(
        self,
        user_address: gl.Address,
        platform: str,
        profile_url: str,
        claim: str
    ) -> str:

        if platform not in self.supported_platforms:
            raise gl.Rollback(f"Platform {platform} not supported")

        if not self._is_domain_whitelisted(profile_url):
            raise gl.Rollback("Domain not whitelisted")

        # Non deterministic web fetch
        profile_content = await gl.nondet.web.render(profile_url, mode="text")

        prompt = f"""
Determine whether the following claim is supported by the provided profile content.

Claim:
"{claim}"

Profile content:
{profile_content[:2000]}

Return strict JSON only:
{{
  "verified": true or false,
  "confidence": 0-100
}}
"""

        result = await gl.nondet.exec_prompt(
            prompt,
            eq_principle=gl.eq_principle.prompt_non_comparative(
                criteria="The output must logically assess whether the claim is supported by the profile content."
            )
        )

        verification = json.loads(result)

        record = {
            "platform": platform,
            "verified": verification["verified"],
            "confidence": verification["confidence"],
            "timestamp": gl.block.number
        }

        users = self.verified_users
        users[user_address] = json.dumps(record)
        self.verified_users = users

        return json.dumps(record)

    # --- public read interface ---

    @gl.public.view
    def is_verified(self, user_address: gl.Address, min_confidence: int = 70) -> bool:
        if user_address not in self.verified_users:
            return False

        data = json.loads(self.verified_users[user_address])
        return data["verified"] and data["confidence"] >= min_confidence

    @gl.public.view
    def get_verification_data(self, user_address: gl.Address) -> str:
        return self.verified_users.get(user_address, "")

    # --- admin controls ---

    @gl.public.write
    def add_platform(self, platform: str) -> None:
        platforms = self.supported_platforms
        platforms.append(platform)
        self.supported_platforms = platforms

    @gl.public.write
    def add_whitelisted_domain(self, domain: str) -> None:
        domains = self.whitelisted_domains
        domains.append(domain)
        self.whitelisted_domains = domains
