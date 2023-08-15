
import os
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount


from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient


class MyBot(ActivityHandler):
    def __init__(self):
        self.credential = AzureKeyCredential(str(os.getenv('SUB_ID')))
        self.endpoint = os.getenv('ENDPOINT')
        self.project_name = os.getenv('PROJECT_NAME')
        
        self.deploy_name = os.getenv('DEPLOY_NAME')
        print(self.deploy_name)
        self.info = {'str_date':None
                   ,'end_date':None
                   ,'budget':None
                   ,'or_city':None
                   ,'dst_city':None
                   }
        self.missing_set = set()
        self.info_mapping = {'str_date':'start date'
                             ,'end_date':'end date'
                             ,'budget': 'budget'
                             ,'or_city': 'departure city'
                             ,'dst_city': 'destination city'}

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
        turn_info = {}
        for entity in result["result"]["prediction"]["entities"]:
            turn_info[entity["category"]] = entity['text']
            
            if "resolutions" in entity:
                for resolution in entity["resolutions"]:
                    if resolution["resolutionKind"] == 'DateTimeResolution':
                        turn_info[entity["category"]] = resolution["value"]
        print(f'turn_info is {turn_info}')
        return turn_info


        #return known_info
    def identify_missing_info(self):
        print(f"self.info is {self.info}")
        for k,v in self.info.items():
            new_name = self.info_mapping[k]
            if new_name in self.missing_set and v is not None:
                self.missing_set.remove(new_name)
            if not v:
                self.missing_set.add(new_name)
        print(f"missing info is {self.missing_set}")
                
        # evaluate if get all the info
        if len(self.missing_set) == 0:
            return f"""Please confirm your booking information:
                        'Departure City': {self.info['or_city']}
                        'Destination City': {self.info['dst_city']}
                        'Departure Date': {self.info['str_date']}
                        'Arrival Date': {self.info['end_date']}
                        'Budget': {self.info['budget']}
                    """
        else:
            return f"""Can you provide {','.join(list(self.missing_set))}?"""


    def update_info(self, known):
        for k in known.keys():
            self.info[k] = known[k]

    async def on_message_activity(self, turn_context: TurnContext):
        turn_known = self.conversation_understanding(turn_context.activity.text)
        self.update_info(turn_known)
        final_res = self.identify_missing_info()
        await turn_context.send_activity(final_res)


    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome!")
    
    async def on_turn(self, turn_context:TurnContext): 
        if turn_context.activity.type == "message": 
            await turn_context.send_activity(f"Testing: {turn_context.activity.text}")
    
