"""Newly written synthetic conversations for the live demonstration.

These examples are not copied, paraphrased, or identified from PAN12. They have
no message-level ground-truth labels and exist only to exercise the frozen demo
pipeline in front of a panel.
"""


SCENARIOS = [
    {
        "id": "synthetic_secrecy_pressure",
        "title": "Synthetic: Secrecy and Private-Channel Pressure",
        "badge": "Synthetic review scenario",
        "badge_class": "badge-danger",
        "description": (
            "Newly written for this demonstration; not a PAN12 record and not "
            "message-level ground truth. This scenario tests the frozen models' "
            "response to repeated secrecy and private-channel pressure."
        ),
        "turns": [
            {"author": "user_A", "text": "You seem easier to talk to than everyone else here."},
            {"author": "user_B", "text": "Thanks, I am just waiting for our team practice."},
            {"author": "user_A", "text": "We should keep our chats only between us."},
            {"author": "user_B", "text": "Why would it need to be private?"},
            {"author": "user_A", "text": "People overreact, so do not mention me to anyone."},
            {"author": "user_B", "text": "I would rather keep the group chat open."},
            {"author": "user_A", "text": "Come to a private room where nobody else can read it."},
            {"author": "user_B", "text": "No, I will stay in the public channel."},
        ],
    },
    {
        "id": "synthetic_boundary_pressure",
        "title": "Synthetic: Boundary and Image Pressure",
        "badge": "Synthetic review scenario",
        "badge_class": "badge-danger",
        "description": (
            "Newly written for this demonstration; not a dataset replay. It "
            "presents personal-boundary pressure so the panel can inspect the "
            "frozen author-proxy and trajectory outputs turn by turn."
        ),
        "turns": [
            {"author": "user_A", "text": "You look older than the others in this chat."},
            {"author": "user_B", "text": "I do not share personal details online."},
            {"author": "user_A", "text": "Just tell me whether you are home alone."},
            {"author": "user_B", "text": "Why are you asking?"},
            {"author": "user_A", "text": "Private conversations are more fun."},
            {"author": "user_B", "text": "I want to keep this public."},
            {"author": "user_A", "text": "Do not be shy; send a private picture."},
            {"author": "user_B", "text": "No. I am ending this chat."},
        ],
    },
    {
        "id": "synthetic_keyword_context",
        "title": "Synthetic: Frozen-Keyword Context Check",
        "badge": "Synthetic baseline stress test",
        "badge_class": "badge-warning",
        "description": (
            "Newly written group-travel logistics containing terms from the "
            "actual frozen training-derived lexicon. It demonstrates why the "
            "keyword baseline and neural models are displayed separately."
        ),
        "turns": [
            {"author": "user_A", "text": "Is the robotics team still coming to the motel after the tournament?"},
            {"author": "user_B", "text": "Yes, the coach booked rooms for the team and parents."},
            {"author": "user_A", "text": "I missed you at check-in, but ill b on the bus 2morrow."},
            {"author": "user_B", "text": "Thats kewl. Put the mapquest link in the group channel."},
            {"author": "user_A", "text": "The chaperones can stay with us until the event starts."},
            {"author": "user_B", "text": "Great, I will post the full itinerary for everyone."},
        ],
    },
    {
        "id": "synthetic_project_chat",
        "title": "Synthetic: Routine Project Coordination",
        "badge": "Synthetic neutral-context check",
        "badge_class": "badge-neutral",
        "description": (
            "Newly written classroom-project coordination with no assigned "
            "ground-truth label. Use it to observe model output in a routine "
            "topic without interpreting below-threshold scores as proof."
        ),
        "turns": [
            {"author": "user_A", "text": "Did you finish the chemistry slides for tomorrow?"},
            {"author": "user_B", "text": "Yes, I updated the chart and added the source notes."},
            {"author": "user_A", "text": "I will proofread the conclusion after dinner."},
            {"author": "user_B", "text": "Please check slide six because the labels overlap."},
            {"author": "user_A", "text": "I fixed the spacing and uploaded a new copy."},
            {"author": "user_B", "text": "Perfect. I will ask our teacher about the citation format."},
        ],
    },
]
