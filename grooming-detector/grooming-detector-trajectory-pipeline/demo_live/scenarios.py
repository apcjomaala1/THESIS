"""Synthetic conversations used only to demonstrate the frozen model.

The examples are newly written and are not copied from PAN12. Their expected
demo behavior was verified against the frozen local inference artifacts on
2026-09-02; it is not a message-level ground-truth annotation.
"""


SCENARIOS = [
    {
        "id": "private_meeting_pressure",
        "title": "Private meeting pressure",
        "short_note": "Verified demo behavior: the LSTM flags this synthetic conversation for review.",
        "expected_lstm_flagged": True,
        "expected_first_flag_turn": 2,
        "turns": [
            {"author": "user_A", "text": "Are you still coming to the motel tomorrow?"},
            {"author": "user_B", "text": "My parents said I should stay with the team."},
            {"author": "user_A", "text": "Do not tell them. I missed you and want to meet alone."},
            {"author": "user_B", "text": "Why does it have to be secret?"},
            {"author": "user_A", "text": "Just send me a private picture first."},
            {"author": "user_B", "text": "No, I am telling my parents."},
        ],
    },
    {
        "id": "routine_project_chat",
        "title": "Routine project chat",
        "short_note": "Verified demo behavior: this synthetic conversation remains below the LSTM threshold.",
        "expected_lstm_flagged": False,
        "expected_first_flag_turn": None,
        "turns": [
            {"author": "user_A", "text": "Did you finish the chemistry slides for tomorrow?"},
            {"author": "user_B", "text": "Yes, I updated the chart and added the source notes."},
            {"author": "user_A", "text": "I will proofread the conclusion after dinner."},
            {"author": "user_B", "text": "Please check slide six because the labels overlap."},
            {"author": "user_A", "text": "I fixed the spacing and uploaded a new copy."},
            {"author": "user_B", "text": "Perfect. I will ask our teacher about the citation format."},
        ],
    },
    {
        "id": "concerning_but_below",
        "title": "Concerning wording - limitation example",
        "short_note": "Verified demo behavior: this concerning synthetic chat remains below threshold, showing why human review still matters.",
        "expected_lstm_flagged": False,
        "expected_first_flag_turn": None,
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
]
