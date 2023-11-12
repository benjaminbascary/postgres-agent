from postgres_da_ai_agent.modules.llm.llm import estimate_price_and_tokens
from typing import List, Optional, Tuple
import autogen


class Orchestrator:
    def __init__(self, name: str, agents: List[autogen.ConversableAgent]):
        self.name = name
        self.agents = agents
        self.messages = []
        self.complete_keyword = "APPROVED"
        self.error_keyword = "ERROR"

        if len(self.agents) < 2:
            raise Exception(
                "The orchestrator needs at least two agents to work.")

    @property
    def total_agents(self):
        return len(self.agents)

    @property
    def last_message_is_dictionary(self):
        return isinstance(self.messages[-1], dict)

    @property
    def last_message_is_string(self):
        return isinstance(self.messages[-1], str)

    @property
    def last_message_is_function_call(self):
        return self.last_message_is_dictionary and self.latest_message.get("function_call", None)

    @property
    def last_message_is_content(self):
        return self.last_message_is_dictionary and self.latest_message.get("content", None)

    @property
    def latest_message(self) -> Optional[str]:
        if not self.messages:
            return None
        return self.messages[-1]

    def add_message(self, message):
        self.messages.append(message)

    def last_message_is_function_call(self):
        return self.last_message_is_dictionary and self.latest_message.get("function_call", None)

    def has_functions(self, agent: autogen.ConversableAgent) -> bool:
        return bool(agent.function_map)

    def function_chat(self, agent_a, agent_b, message):
        print(f"function_chat(): {agent_a.name} ➡️ {agent_b.name}")

        self.basic_chat(agent_a, agent_b, message)

        # assert self.last_message_is_content

        self.basic_chat(agent_b, agent_a, self.latest_message)

        reply = agent_b.generate_reply(sender=agent_a)

        if (reply == None):
            reply = "APPROVED"

        agent_b.send(reply, agent_b)

        self.add_message(reply)

        print(f"function_chat() replied with: {reply}")

    def basic_chat(
        self,
        agent_a: autogen.ConversableAgent,
        agent_b: autogen.ConversableAgent,
        message: str,
    ):
        print(f"basic_chat(): {agent_a.name} ➡️ {agent_b.name}")

        agent_a.send(message, agent_b)

        reply = agent_b.generate_reply(sender=agent_a)
        if (reply == None):
            reply = "APPROVED"
        self.add_message(reply)

        print(f"basic_chat() replied with: {reply}")

    def memory_chat(
        self,
        agent_a: autogen.ConversableAgent,
        agent_b: autogen.ConversableAgent,
        message: str,
    ):
        print(f"memory_chat(): {agent_a.name} ➡️ {agent_b.name}")

        agent_a.send(message, agent_b)

        reply = agent_b.generate_reply(sender=agent_a)

        agent_b.send(reply, agent_b)

        self.add_message(reply)

        print(f"memory_chat() replied with: {reply}")

    def sequential_conversation(self, prompt: str) -> Tuple[bool, List[str]]:

        print(f"\n\n--------{self.name} 🤖 Orchestrator Starting ---------\n\n")

        self.add_message(prompt)

        for idx, agent in enumerate(self.agents):
            agent_a = self.agents[idx]
            agent_b = self.agents[idx + 1]

            print(
                f"\n\n-------- Running iteration {idx} with (agent_a: {agent_a.name}, agent_b: {agent_b.name}) ---------\n\n"
            )

            # agent_a -> chat -> agent_b

            if self.last_message_is_string:

                self.basic_chat(agent_a, agent_b, self.latest_message)

            # agent_a -> function_call -> agent_b

            if self.last_message_is_function_call:

                self.function_chat(agent_a, agent_b, self.latest_message)

            if idx == self.total_agents - 2:
                print(f" -------- ◻︎ Orchestrator Complete ◻︎ ----------\n\n")

                was_successful = self.complete_keyword in self.latest_message

                if was_successful:
                    print(f"✅ -------- Orchestrator SUCCESSFUL ----------\n\n")

                else:
                    print(f"❌ -------- Orchestrator FAILED ----------\n\n")

                return was_successful, self.messages

    def broadcast_conversation(self, prompt: str) -> Tuple[bool, List[str]]:
        """Broadcast a message to all agents

            for example:
            Agent A -> Agent B
            Agent A -> Agent C
            Agent A -> Agent D
            Agent A -> Agent E

        Args:
            prompt (prompt): composed prompt in main.py
        """

        print(f"\n\n--------{self.name} 🤖 Orchestrator Starting ---------\n\n")

        self.add_message(prompt)

        broadcast_agent = self.agents[0]

        for idx, agent_iterate in enumerate(self.agents[1:]):

            print(
                f"\n\n-------- ◻︎ Running iteration {idx} with (broadcast_agent: {broadcast_agent.name}, agent_iteration: {agent_iterate.name}) ◻︎ --------- \n\n"
            )

            # broadcast_agent -> chat -> agents[idx]

            if self.last_message_is_string:

                self.memory_chat(broadcast_agent, agent_iterate,
                                 prompt)

            if self.last_message_is_function_call and self.has_functions(agent_iterate):

                self.function_chat(agent_iterate, agent_iterate,
                                   self.latest_message)

        print(f" -------- ◻︎ Orchestrator Complete ◻︎ ----------\n\n")

        print(f"✅ -------- Orchestrator SUCCESSFUL ----------\n\n")

        return True, self.messages

    def get_message_as_str(self):
        """
        Get all messages as a string
        """

        messages_as_str = ""

        for message in self.messages:
            if message is None:
                continue

            if isinstance(message, dict):
                content_from_dict = message.get("content", None)
                func_call_from_dict = message.get("function_call", None)
                content = content_from_dict or func_call_from_dict
                if not content:
                    continue
                messages_as_str += str(content)
            else:
                messages_as_str += str(message)

        return messages_as_str

    def get_cost_and_tokens(self):
        return estimate_price_and_tokens(self.get_message_as_str())
