"""Implementation of the adviser-approved author-derived endpoint.

This package is deliberately isolated from the historical ``is_suspicious``
pipeline.  Its public modules enforce the locked connected-author partitions,
stable row identifiers, conversation-only Layer 2 supervision, independently
tuned comparison methods, a predeclared LSTM search, and an explicit final-test
gate. Downstream implementation details are preparation, not a claim that each
choice was separately adviser-approved.
"""

PROTOCOL_VERSION = "1.0.0"
