from .tables import Agent
from dataclasses import dataclass
from secrets import token_bytes
from .exceptions import AgentNotExist, InvalidToken

@dataclass()
class AgentMeta:
    uuid: str
    name: str

async def create_new_agent(agent_name: str) -> tuple[str, AgentMeta]:
    """
    Create new agent with name

    Args:
        agent_name: name or description to give the agent

    Returns:
        tuple[str, AgentMeta]
            A tuple containing:
            - str: login token for agent
            - AgentMeta: additional metadata, including uuid of agent

    Raises:
        None

    """
    new_agent = Agent(name=agent_name, token=token_bytes(32).hex())
    await Agent.insert(new_agent)
    return new_agent.token, AgentMeta(name=new_agent.name, uuid=new_agent.uuid)

async def authenticate_agent(uuid: str, token: str) -> AgentMeta:
    """
    Authenticate an agent with uuid and token

    Args:
        uuid: generated uuid of agent 
        token: generated token of agent

    Returns:
        AgentMeta: metadata of just authenticated agent

    Raises:
        AgentNotExist: agent of given uuid does not exist
        InvalidToken: agent with valid uuid is attempting to use an invalid token
    """
    agent = await Agent.select(Agent.name, Agent.token).where(Agent.uuid == uuid).first()
    if agent is None:
        raise AgentNotExist()

    if agent["token"] != token:
        raise InvalidToken()

    meta = AgentMeta(
            name = agent["name"],
            uuid = uuid
            )
    return meta
