
import os
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount


from azure.core.credentials import AzureKeyCredential
#from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from azure.ai.language.conversations import ConversationAnalysisClient


class MyBot(ActivityHandler):
    def __init__(self):
        self.credential = AzureKeyCredential(os.getenv('SUB_ID'))
        self.endpoint = os.getenv('ENDPOINT')
        self.project_name = os.getenv('PROJECT_NAME')
        self.deploy_name = os.getenv('DEPLOY_NAME')
    # See https://aka.ms/about-bot-activity-message to learn more about the message and other activity types.

    def conversation_understanding(self,query):
        client = ConversationAnalysisClient(self.endpoint, self.credential)

        with client:
            result = client.analyze_conversation(
                task={
                    "kind": "Conversation",
                    "analysisInput": {
                        "conversationItem": {
                            "participantId": "1",
                            "id": "1",
                            "modality": "text",
                            "language": "en",
                            "text": query
                        },
                        "isLoggingEnabled": False
                    },
                    "parameters": {
                        "projectName": self.project_name,
                        "deploymentName": self.deploy_name,
                        "verbose": True
                    }
                }
            )
        known_info = {}
        for entity in result["result"]["prediction"]["entities"]:
            known_info[entity["category"]] = entity['text']
            
            if "resolutions" in entity:
                for resolution in entity["resolutions"]:
                    if resolution["resolutionKind"] == 'DateTimeResolution':
                        known_info[entity["category"]] = resolution["value"]
                    
        return known_info
    

    async def on_message_activity(self, turn_context: TurnContext):
        #print(turn_context.activity.text)
        res = self.conversation_understanding(turn_context.activity.text)
        await turn_context.send_activity(f"You said '{res}'")

    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome!")
    
    
    
