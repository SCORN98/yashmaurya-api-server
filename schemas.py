from pydantic import BaseModel

# यह एक नियम है: जब भी कोई बदलाव लागू (Apply) होगा, तो ये जानकारी चाहिए होगी
class ApplyRequest(BaseModel):
    proposal_id: str   # प्रपोजल का नाम या ID
    user_name: str     # किसने बदलाव किया
    force_apply: bool = False  # क्या जबरदस्ती बदलाव करना है?