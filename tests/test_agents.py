import pytest
import control
import secrets

@pytest.mark.asyncio
async def test_agent_login_flow():
    token, agent = await control.create_new_agent("Test Agent 1")
    await control.authenticate_agent(agent.uuid, token)

    with pytest.raises(control.AgentNotExist):
        await control.authenticate_agent("67637778-b3de-4daf-ac26-529573230ed7", token)

    with pytest.raises(control.InvalidToken):
        await control.authenticate_agent(agent.uuid, secrets.token_bytes(32).hex())
