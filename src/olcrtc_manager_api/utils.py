wordlist = [
"Able", "About", "Above", "Accept", "Access", "Action", "Active", "Actual", "Add", "Address",
"Advance", "Advice", "Afford", "After", "Again", "Against", "Agree", "Ahead", "Alert", "Allow",
"Almost", "Along", "Already", "Also", "Always", "Amount", "Analyze", "Angle", "Answer", "Appear",
"Apply", "Area", "Argue", "Around", "Arrange", "Article", "Aspect", "Assist", "Assume", "Attack",
"Attempt", "Attend", "Authority", "Available", "Average", "Avoid", "Aware", "Balance", "Basic",
"Because", "Become", "Before", "Begin", "Behind", "Believe", "Benefit", "Between", "Beyond",
"Block", "Build", "Business", "Calculate", "Cancel", "Capacity", "Capture", "Care", "Cause",
"Center", "Change", "Charge", "Check", "Choice", "Choose", "Circle", "Claim", "Clear", "Close",
"Code", "Collect", "Combine", "Comment", "Common", "Compare", "Complete", "Concern", "Condition",
"Connect", "Consider", "Contact", "Contain", "Continue", "Control", "Convert", "Correct",
"Create", "Credit", "Culture", "Current", "Custom", "Damage", "Data", "Decide", "Deliver",
"Demand", "Depend", "Describe", "Design", "Detail", "Develop", "Different", "Direct", "Discuss",
"Display", "Divide", "Domain", "Double", "Draw", "Drive", "Effect", "Effort", "Enable",
"End", "Energy", "Engage", "Enhance", "Equal", "Establish", "Estimate", "Event", "Evidence",
"Example", "Exchange", "Exist", "Expand", "Expect", "Experience", "Explain", "Explore",
"Express", "Extend", "Factor", "Feature", "Focus", "Follow", "Force", "Form", "Function",
"Generate", "Goal", "Group", "Grow", "Guide", "Handle", "Help", "Identify", "Image", "Impact",
"Implement", "Include", "Increase", "Indicate", "Individual", "Industry", "Inform", "Input",
"Inside", "Install", "Instance", "Interest", "Interpret", "Introduce", "Issue", "Item", "Join",
"Keep", "Know", "Label", "Large", "Last", "Lead", "Learn", "Level", "Limit", "Link", "List",
"Local", "Logic", "Maintain", "Major", "Make", "Manage", "Market", "Measure", "Method", "Model"
]

import random, string

from config import settings

def getRoomId():
    if settings.OLCRTC_CARRIER == "jitsi":
        return settings.OLCRTC_JITSI_URL + "/" + "".join([wordlist[random.randint(0, len(wordlist) - 1)] for _ in range(5)])  # pyright: ignore[reportOptionalOperand]
    else:
        return settings.OLCRTC_ROOM_ID


def getRandomKey():
    return "".join([string.hexdigits[random.randint(0, 15)] for _ in range(64)])