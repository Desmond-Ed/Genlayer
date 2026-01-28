# v0.1.0
# { "Depends": "py-genlayer:latest" }

from genlayer import *
import json


class SocialProofLibrary(gl.Contract):

    verified_users: TreeMap[gl.Address, str]
    supported_platforms: DynArray[str]

    def __init__(self):
        self.supported_platforms = ["github", "twitter", "linkedin"]
        self.verified_users = TreeMap[gl.Address, str]()

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

        profile_content = await gl.nondet.web.render(profile_url, mode="text")

        prompt = f"""
Verify this claim: "{claim}"

Based on the following {platform} profile content:
{profile_content[:2000]}

Return strict JSON only:
{{
  "verified": true or false,
  "confidence": 0-100,
  "evidence": ["proof1", "proof2"]
}}
"""

        result = await gl.nondet.exec_prompt(prompt)
        
        try:
            verification = json.loads(result)
        except json.JSONDecodeError:
            raise gl.Rollback(f"Failed to parse verification result: {result[:100]}")

        record = {
            "platform": platform,
            "verified": verification["verified"],
            "confidence": verification["confidence"],
            "timestamp": gl.block.number
        }

        self.verified_users[user_address] = json.dumps(record)

        return json.dumps(record)

    @gl.public.view
    def is_verified(self, user_address: gl.Address, min_confidence: int = 70) -> bool:
        if user_address not in self.verified_users:
            return False

        data = json.loads(self.verified_users[user_address])
        return data["verified"] and data["confidence"] >= min_confidence

    @gl.public.view
    def get_verification_data(self, user_address: gl.Address) -> str:
        return self.verified_users.get(user_address, "")

    @gl.public.write
    def add_platform(self, platform: str) -> None:
        if platform not in self.supported_platforms:
            self.supported_platforms.append(platform)

def main() -> SocialProofLibrary:
    return SocialProofLibrary()
