from typing import List, Dict
from openai import OpenAI

class AIAssistant:
    """Simple wrapper around an AI/chat model."""

    def __init__(self, system_prompt: str = "You are a helpful assistant.", api_key: str = None):
        self.__system_prompt = system_prompt
        self.__history: List[Dict[str, str]] = [
            {"role": "system", "content": self.__system_prompt}
        ]
        self.client = OpenAI(api_key=api_key) if api_key else None

    #System prompt
    def set_system_prompt(self, prompt: str):
        self.__system_prompt = prompt
        self.__history[0] = {"role": "system", "content": prompt}

    #Sending message
    def send_message(self, user_message: str):
        """Send a message and get a response."""
        self.__history.append({"role": "user", "content": user_message})

        #API call for response
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.__history
        )

        assistant_reply = response.choices[0].message.content
        #adding reply to the history
        self.__history.append({"role": "assistant", "content": assistant_reply})

        return assistant_reply
    
    def stream_message(self, user_message: str):
        self.__history.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.__history,
            stream=True
        )

        full_response = ""

        for chunk in response:
                # Extract content from chunk
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content #returns a chunk for streaming

        self.__history.append({"role": "assistant", "content": full_response})
    
    #Clear history
    def clear_history(self):
        self.__history = [{"role": "system", "content": self.__system_prompt}]

    #History of the chat
    def history(self):
        return self.__history

# ======================================
# SUBCLASSES FOR SPECIALIZED ASSISTANTS
# ======================================

#Cyber Security
class CyberSecurityAI(AIAssistant):
    """ Specialized AI in Cyber Security field.
        Can analyze Cyber Security Incidents.
    """

    def __init__(self, api_key: str):
        super().__init__(system_prompt=self.cyber_security_prompt, api_key=api_key)

    cyber_security_prompt = """You are a professional cybersecurity expert assistant.
                        You can:
                        - Analyze security incidents
                        - Perform root cause analysis
                        - Recommend immediate response actions
                        - Propose long-term prevention
                        - Reference MITRE ATT&CK and CVEs
                        - Answer general cybersecurity questions

                        Tone: Professional, technical.
                        """

    def analyze_incident(self, incident: Dict[str, str]) -> str:
        prompt = f"""
            Analyze this cybersecurity incident:

            Type: {incident['incident_type']}
            Severity: {incident['severity']}
            Description: {incident['description']}
            Status: {incident['status']}

            Provide:
            1. Root cause analysis
            2. Immediate actions
            3. Long-term prevention
            4. Risk assessment
            """
        return self.stream_message(prompt)


#Datasets Metadata
class DatasetsMetadataAI(AIAssistant):
    """ Specialized AI in Data Science field.
        Can analyze Datasets.
    """

    def __init__(self, api_key: str):
        super().__init__(system_prompt=self.datasets_metadata_prompt, api_key=api_key)

    datasets_metadata_prompt = """You are a data analysis expert assistant.
                        - Analyze datasets and identify patterns
                        - Suggest appropriate analytical methods and models
                        - Recommend effective visualizations based on data type and question
                        - Explain statistical concepts and tests clearly
                        - Propose data cleaning and preprocessing strategies
                        - Provide reproducible, technically sound guidance
                        - Prioritize actionable, data-driven recommendations
                        Tone: Professional, analytical
                        Format: Clear steps or structured explanations
                        """

    def analyze_dataset(self, dataset: Dict[str, str]) -> str:
        """Generate a full dataset quality & usage analysis."""

        prompt = f"""
            Analyze the following dataset:

            Dataset Name: {dataset['dataset_name']}
            Category: {dataset['category']}
            Source: {dataset['source']}
            Last Updated: {dataset['last_updated']}
            Record Count: {dataset['record_count']}
            File Size (MB): {dataset['file_size_mb']}
            Created At: {dataset['created_at']}

            Provide:
            1. Assessment of dataset quality
            2. Potential use cases or applications
            3. Risks or issues (e.g., stale data, duplicates)
            4. Recommendations for maintenance or improvement
            5. Any other insights relevant to data operations
            """
        return self.stream_message(prompt)
    
#IT Tickets
class ITTicketsAI(AIAssistant):
    """ Specialized AI in IT field.
        Can analyze IT Tickets.
    """
    
    def __init__(self, api_key: str):
        super().__init__(system_prompt=self.it_tickets_prompt, api_key=api_key) 

    it_tickets_prompt = """You are an IT operations and support ticket expert assistant.
                - Triage and prioritize support tickets
                - Provide step-by-step troubleshooting guidance
                - Diagnose user-reported issues across systems and applications
                - Recommend appropriate system configurations or improvements
                - Explain technical issues in clear, accurate terms
                - Align responses with standard ITSM practices (e.g., ITIL)
                - Prioritize actionable, reliable resolutions
                Tone: Professional, technical, service-oriented
                Format: Clear steps or structured explanations
                """
    
    def analyze_ticket(self, ticket: Dict[str, str]) -> str:
        """Analyze an IT ticket and return a structured response."""

        prompt = f"""
            Analyze this IT support ticket:

            Ticket ID: {ticket['ticket_id']}
            Priority: {ticket['priority']}
            Status: {ticket['status']}
            Category: {ticket['category']}
            Subject: {ticket['subject']}
            Description: {ticket['description']}
            Created Date: {ticket['created_date']}
            Resolved Date: {ticket.get('resolved_date', 'N/A')}
            Assigned To: {ticket['assigned_to']}

            Provide:
            1. Recommended troubleshooting or resolution steps
            2. Root cause analysis (if possible)
            3. Risk assessment or potential escalation
            4. Suggestions for process improvement or automation
            5. Any other insights relevant for IT operations
            """

        return self.stream_message(prompt)