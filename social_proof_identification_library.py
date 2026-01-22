# { "Depends": "py-genlayer:test" }

from genlayer import *
import json
import typing

@gl.contract
class SocialProofIdentificationLibrary:
    """
    Reusable verification library that other contracts can call.
    Provides identity verification as a service.
    """
    
    verified_users: TreeMap[gl.Address, dict]
    
    supported_platforms: DynArray[str]
    
    registered_contracts: DynArray[gl.Address]
    
    def __init__(self):
        self.supported_platforms = ["github", "twitter", "linkedin"]
    
    @gl.public.view
    def is_verified(
        self, 
        user_address: str, 
        min_confidence: int = 70
    ) -> bool:
        """
        Quick check if a user is verified.
        Other contracts call this to gate access.
        """
        address = gl.Address(user_address)
        if address not in self.verified_users:
            return False
        
        user_data = self.verified_users[address]
        return (
            user_data.get("verified", False) and 
            user_data.get("confidence", 0) >= min_confidence
        )
    
    @gl.public.view
    def get_verification_data(self, user_address: str) -> TreeMap[str, typing.Any]:
        """
        Get full verification details.
        Returns: platform, verified status, confidence, evidence, timestamp
        """
        address = gl.Address(user_address)
        if address in self.verified_users:
            return self.verified_users[address]
        else:
            return {
                "verified": False,
                "message": "No verification found"
            }
    
    @gl.public.view
    def get_supported_platforms(self) -> DynArray[str]:
        """
        Returns list of supported platforms.
        """
        return self.supported_platforms
    
    
    @gl.public.write
    async def verify_social_proof(
        self,
        platform: str,
        profile_url: str,
        claim_to_verify: str
    ) -> TreeMap[str, typing.Any]:
        """
        Main verification function.
        Fetches profile, analyzes with LLM, stores result.
        """
        if platform not in self.supported_platforms:
            return {
                "verified": False,
                "error": f"Platform {platform} not supported"
            }
        
        try:
            profile_content = await gl.get_webpage(profile_url, mode='text')
        except Exception as e:
            return {
                "verified": False,
                "error": f"Failed to fetch profile: {str(e)}"
            }
        
        prompt = f"""
Analyze this {platform} profile to verify a claim.

PROFILE URL: {profile_url}
PROFILE CONTENT: {profile_content[:3000]}

CLAIM: "{claim_to_verify}"

Determine if this claim is supported by the profile evidence.

Respond in JSON format:
{{
    "verified": true/false,
    "confidence": 0-100,
    "reasoning": "brief explanation",
    "evidence": ["proof1", "proof2"]
}}
"""
        result = await gl.exec_prompt(prompt)
        
        try:
            verification_data = json.loads(result)
        except:
            verification_data = {
                "verified": False,
                "confidence": 0,
                "reasoning": "Failed to parse verification",
                "evidence": []
            }
        
        self.verified_users[gl.message.sender_address] = {
            "platform": platform,
            "profile_url": profile_url,
            "claim": claim_to_verify,
            "verified": verification_data.get("verified", False),
            "confidence": verification_data.get("confidence", 0),
            "reasoning": verification_data.get("reasoning", ""),
            "evidence": verification_data.get("evidence", []),
            "timestamp": gl.block.number
        }
        
        return verification_data
    
    
    @gl.public.write
    def add_platform(self, platform: str) -> None:
        """
        Extend supported platforms.
        """
        if platform not in self.supported_platforms:
            self.supported_platforms.append(platform)
    
    @gl.public.write
    def register_client_contract(self) -> None:
        """
        Allow other contracts to register as clients for tracking.
        """
        if gl.message.sender_address not in self.registered_contracts:
            self.registered_contracts.append(gl.message.sender_address)