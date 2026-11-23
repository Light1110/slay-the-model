"""Apply relic upgrades to cards offered for permanent acquisition."""


def preview_deck_card(card, relics):
    """Apply the player's obtain-preview upgrades to the offered card."""
    for relic in relics:
        hook = getattr(relic, "should_upgrade_added_card", None)
        if hook and hook(card, "deck") and card.can_upgrade():
            card.upgrade()
