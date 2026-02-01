# Common Potions
@register_potion("Ancient Potion")
class AncientPotion(Potion):
    def __init__(self):
        super().__init__("Ancient Potion", "Uncommon", "The Spire", 1)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Ancient Potion"
        player.artifact += self.potion_yield
        self.uses_remaining -= 1
        return f"Ancient Potion granted {self.potion_yield} Artifact"

@register_potion("Attack Potion")
class AttackPotion(Potion):
    def __init__(self):
        super().__init__("Attack Potion", "Common", "The Spire", 1)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Attack Potion"
        from game.cards.registry import list_registered_cards, create_card
        attack_cards = []
        for card_id in list_registered_cards():
            card = create_card(card_id)
            if getattr(card, "type", "").lower() == "attack":
                namespace = getattr(player, "namespace", None)
                if namespace and not card_id.startswith(f"{namespace}.") and not card_id.startswith("colorless."):
                    continue
                attack_cards.append(card_id)

        if not attack_cards:
            return "No attack cards available"

        chosen_card = random.choice(attack_cards)
        player.hand.append(f"{chosen_card}|cost=0")
        self.uses_remaining -= 1
        card = create_card(chosen_card)
        return f"Attack Potion added {card.name} to hand (costs 0 energy)"

class BlockPotion(Potion):
    def __init__(self):
        super().__init__("Block Potion", "Common", "The Spire", 12)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Block Potion"
        player.gain_block(self.potion_yield)
        self.uses_remaining -= 1
        return f"Block Potion granted {self.potion_yield} Block"

class BloodPotion(Potion):
    def __init__(self):
        super().__init__("Blood Potion", "Common", "Ironclad")

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Blood Potion"
        heal_amount = int(player.max_health * 0.2)
        old_health = player.health
        player.health = min(player.max_health, player.health + heal_amount)
        actual_heal = player.health - old_health
        self.uses_remaining -= 1
        return f"Blood Potion healed {actual_heal} HP (20% of max)"

class ColorlessPotion(Potion):
    def __init__(self):
        super().__init__("Colorless Potion", "Common", "The Spire")

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Colorless Potion"
        from game.cards.registry import list_registered_cards, create_card
        colorless_cards = []
        for card_id in list_registered_cards():
            if card_id.startswith("colorless."):
                colorless_cards.append(card_id)

        if not colorless_cards:
            return "No colorless cards available"

        chosen_cards = random.sample(colorless_cards, min(3, len(colorless_cards)))
        chosen_card = random.choice(chosen_cards)
        player.hand.append(f"{chosen_card}|cost=0")
        self.uses_remaining -= 1
        card = create_card(chosen_card)
        return f"Colorless Potion added {card.name} to hand (costs 0 energy)"

class DexterityPotion(Potion):
    def __init__(self):
        super().__init__("Dexterity Potion", "Common", "The Spire", 2)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Dexterity Potion"
        from game.powers.registry import create_power
        dex_power = create_power("Dexterity", amount=self.potion_yield)
        player.add_power(dex_power)
        self.uses_remaining -= 1
        return f"Dexterity Potion granted {self.potion_yield} Dexterity"

class Elixir(Potion):
    def __init__(self):
        super().__init__("Elixir", "Common", "Ironclad")

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Elixir"
        cards_exhausted = 0
        for card_id in list(player.hand):
            from game.cards.registry import create_card
            card = create_card(card_id)
            if not getattr(card, "exhaust", False):
                player.hand.remove(card_id)
                player.exhaust_pile.append(card_id)
                cards_exhausted += 1
        self.uses_remaining -= 1
        return f"Elixir exhausted {cards_exhausted} cards from hand"

class EnergyPotion(Potion):
    def __init__(self):
        super().__init__("Energy Potion", "Common", "The Spire", 2)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Energy Potion"
        player.energy += self.potion_yield
        self.uses_remaining -= 1
        return f"Energy Potion granted {self.potion_yield} Energy"

class FearPotion(Potion):
    def __init__(self):
        super().__init__("Fear Potion", "Common", "The Spire", 3)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Fear Potion"
        from game.powers.registry import create_power
        vulnerable_power = create_power("Vulnerable", duration=self.potion_yield)
        # Apply to all enemies
        for enemy in game_state.current_enemies:
            enemy.add_power(vulnerable_power)
        self.uses_remaining -= 1
        return f"Fear Potion applied {self.potion_yield} Vulnerable to all enemies"

class FirePotion(Potion):
    def __init__(self):
        super().__init__("Fire Potion", "Common", "The Spire", 20)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Fire Potion"
        total_damage = 0
        for enemy in game_state.current_enemies:
            enemy.health -= self.potion_yield
            total_damage += self.potion_yield
        game_state.remove_dead_enemies()
        self.uses_remaining -= 1
        return f"Fire Potion dealt {total_damage} damage to all enemies"

class FocusPotion(Potion):
    def __init__(self):
        super().__init__("Focus Potion", "Common", "Defect", 2)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Focus Potion"
        player.focus += self.potion_yield
        self.uses_remaining -= 1
        return f"Focus Potion granted {self.potion_yield} Focus"

class FruitJuice(Potion):
    def __init__(self):
        super().__init__("Fruit Juice", "Rare", "The Spire", 5)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Fruit Juice"
        player.max_health += self.potion_yield
        player.health += self.potion_yield
        self.uses_remaining -= 1
        return f"Fruit Juice increased Max HP by {self.potion_yield}"

class PoisonPotion(Potion):
    def __init__(self):
        super().__init__("Poison Potion", "Common", "Silent", 6)

    def use(self, player, entities):
        if not self.can_use(player, entities) or not game_state.current_enemies:
            return "Cannot use Poison Potion"
        target = random.choice(game_state.current_enemies)
        from game.powers.registry import create_power
        poison_power = create_power("Poison", duration=self.potion_yield)
        target.add_power(poison_power)
        self.uses_remaining -= 1
        return f"Poison Potion applied {self.potion_yield} Poison to {getattr(target, 'name', 'enemy')}"

class PotionOfCapacity(Potion):
    def __init__(self):
        super().__init__("Potion of Capacity", "Common", "Defect", 2)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Potion of Capacity"
        player.gain_orb_slots(self.potion_yield)
        self.uses_remaining -= 1
        return f"Potion of Capacity granted {self.potion_yield} Orb slots"

class PowerPotion(Potion):
    def __init__(self):
        super().__init__("Power Potion", "Common", "The Spire", 1)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Power Potion"
        from game.cards.registry import list_registered_cards, create_card
        power_cards = []
        for card_id in list_registered_cards():
            card = create_card(card_id)
            if getattr(card, "type", "").lower() == "power":
                namespace = getattr(player, "namespace", None)
                if namespace and not card_id.startswith(f"{namespace}.") and not card_id.startswith("colorless."):
                    continue
                power_cards.append(card_id)

        if not power_cards:
            return "No power cards available"

        chosen_card = random.choice(power_cards)
        player.hand.append(f"{chosen_card}|cost=0")
        self.uses_remaining -= 1
        card = create_card(chosen_card)
        return f"Power Potion added {card.name} to hand (costs 0 energy)"

class SkillPotion(Potion):
    def __init__(self):
        super().__init__("Skill Potion", "Common", "The Spire", 1)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Skill Potion"
        from game.cards.registry import list_registered_cards, create_card
        skill_cards = []
        for card_id in list_registered_cards():
            card = create_card(card_id)
            if getattr(card, "type", "").lower() == "skill":
                namespace = getattr(player, "namespace", None)
                if namespace and not card_id.startswith(f"{namespace}.") and not card_id.startswith("colorless."):
                    continue
                skill_cards.append(card_id)

        if not skill_cards:
            return "No skill cards available"

        chosen_card = random.choice(skill_cards)
        player.hand.append(f"{chosen_card}|cost=0")
        self.uses_remaining -= 1
        card = create_card(chosen_card)
        return f"Skill Potion added {card.name} to hand (costs 0 energy)"

class SpeedPotion(Potion):
    def __init__(self):
        super().__init__("Speed Potion", "Common", "The Spire", 5)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Speed Potion"
        from game.powers.registry import create_power
        dex_power = create_power("Dexterity", amount=self.potion_yield)
        player.add_power(dex_power)
        # Schedule loss for end of turn
        player.pending_lose_dexterity = getattr(player, 'pending_lose_dexterity', 0) + self.potion_yield
        self.uses_remaining -= 1
        return f"Speed Potion granted {self.potion_yield} Dexterity (lose at end of turn)"

class StrengthPotion(Potion):
    def __init__(self):
        super().__init__("Strength Potion", "Common", "The Spire", 2)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Strength Potion"
        from game.powers.registry import create_power
        str_power = create_power("Strength", amount=self.potion_yield)
        player.add_power(str_power)
        self.uses_remaining -= 1
        return f"Strength Potion granted {self.potion_yield} Strength"

class SwiftPotion(Potion):
    def __init__(self):
        super().__init__("Swift Potion", "Common", "The Spire", 3)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Swift Potion"
        player.draw_cards(self.potion_yield)
        self.uses_remaining -= 1
        return f"Swift Potion drew {self.potion_yield} cards"

class WeakPotion(Potion):
    def __init__(self):
        super().__init__("Weak Potion", "Common", "The Spire", 3)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Weak Potion"
        from game.powers.registry import create_power
        weak_power = create_power("Weak", duration=self.potion_yield)
        # Apply to all enemies
        for enemy in game_state.current_enemies:
            enemy.add_power(weak_power)
        self.uses_remaining -= 1
        return f"Weak Potion applied {self.potion_yield} Weak to all enemies"

# Uncommon Potions
class BlessingOfTheForge(Potion):
    def __init__(self):
        super().__init__("Blessing of the Forge", "Uncommon", "The Spire")

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Blessing of the Forge"
        for card_id in player.hand:
            from game.cards.registry import create_card
            card = create_card(card_id)
            card.upgrade()
        self.uses_remaining -= 1
        return "Blessing of the Forge upgraded all cards in hand"

class CultistPotion(Potion):
    def __init__(self):
        super().__init__("Cultist Potion", "Rare", "The Spire", 1)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Cultist Potion"
        from game.powers.registry import create_power
        str_power = create_power("Strength", amount=self.potion_yield)
        player.add_power(str_power)
        # This strength lasts until end of combat
        self.uses_remaining -= 1
        return f"Cultist Potion granted {self.potion_yield} Strength per turn"

class CunningPotion(Potion):
    def __init__(self):
        super().__init__("Cunning Potion", "Uncommon", "Silent", 3)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Cunning Potion"
        for _ in range(self.potion_yield):
            player.hand.append("colorless.Shiv+1")
        self.uses_remaining -= 1
        return f"Cunning Potion added {self.potion_yield} upgraded Shivs to hand"

class DistilledChaos(Potion):
    def __init__(self):
        super().__init__("Distilled Chaos", "Uncommon", "The Spire", 3)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Distilled Chaos"
        for _ in range(self.potion_yield):
            if player.draw_pile:
                card_id = player.draw_pile.pop()
                player.hand.append(card_id)
                from game.cards.registry import create_card
                card = create_card(card_id)
                # Play the card automatically
                if hasattr(card, 'play') and callable(card.play):
                    card.play()
            else:
                break
        self.uses_remaining -= 1
        return f"Distilled Chaos played top {self.potion_yield} cards from draw pile"

class DuplicationPotion(Potion):
    def __init__(self):
        super().__init__("Duplication Potion", "Uncommon", "The Spire", 1)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Duplication Potion"
        player.duplicate_next_card = True
        self.uses_remaining -= 1
        return "Duplication Potion: Next card will be played twice"

class EssenceOfSteel(Potion):
    def __init__(self):
        super().__init__("Essence of Steel", "Uncommon", "The Spire", 4)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Essence of Steel"
        from game.powers.registry import create_power
        plated_armor = create_power("Plated Armor", amount=self.potion_yield)
        player.add_power(plated_armor)
        self.uses_remaining -= 1
        return f"Essence of Steel granted {self.potion_yield} Plated Armor"

class EssenceOfDarkness(Potion):
    def __init__(self):
        super().__init__("Essence of Darkness", "Rare", "Defect")

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Essence of Darkness"
        # Channel 1 Dark orb for each orb slot
        player.channel_orb("Dark", amount=len(player.orbs))
        self.uses_remaining -= 1
        return f"Essence of Darkness channeled {len(player.orbs)} Dark orbs"

class ExplosivePotion(Potion):
    def __init__(self):
        super().__init__("Explosive Potion", "Uncommon", "The Spire", 10)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Explosive Potion"
        total_damage = 0
        for enemy in game_state.current_enemies:
            enemy.health -= self.potion_yield
            total_damage += self.potion_yield
        game_state.remove_dead_enemies()
        self.uses_remaining -= 1
        return f"Explosive Potion dealt {total_damage} damage to all enemies"

class FairyInABottle(Potion):
    def __init__(self):
        super().__init__("Fairy in a Bottle", "Rare", "The Spire")

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Fairy in a Bottle"
        player.fairy_protection = True
        self.uses_remaining -= 1
        return "Fairy in a Bottle: Will heal to 30% HP when near death"

class FlexPotion(Potion):
    def __init__(self):
        super().__init__("Flex Potion", "Common", "The Spire", 5)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Flex Potion"
        from game.powers.registry import create_power
        str_power = create_power("Strength", amount=self.potion_yield)
        player.add_power(str_power)
        # Schedule loss for end of turn
        player.pending_lose_strength = getattr(player, 'pending_lose_strength', 0) + self.potion_yield
        self.uses_remaining -= 1
        return f"Flex Potion granted {self.potion_yield} Strength (lose at end of turn)"

class GamblersBrew(Potion):
    def __init__(self):
        super().__init__("Gamblers Brew", "Uncommon", "The Spire")

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Gamblers Brew"
        discarded = len(player.hand)
        player.discard_pile.extend(player.hand)
        player.hand = []
        player.draw_cards(discarded)
        self.uses_remaining -= 1
        return f"Gambler's Brew discarded {discarded} cards and drew {discarded} new ones"

class GhostInAJar(Potion):
    def __init__(self):
        super().__init__("Ghost in a Jar", "Uncommon", "Silent", 1)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Ghost in a Jar"
        from game.powers.registry import create_power
        intangible = create_power("Intangible", duration=self.potion_yield)
        player.add_power(intangible)
        self.uses_remaining -= 1
        return f"Ghost in a Jar granted {self.potion_yield} Intangible"

class HeartOfIron(Potion):
    def __init__(self):
        super().__init__("Heart Of Iron", "Rare", "Ironclad", 6)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Heart Of Iron"
        from game.powers.registry import create_power
        metallicize = create_power("Metallicize", amount=self.potion_yield)
        player.add_power(metallicize)
        self.uses_remaining -= 1
        return f"Heart Of Iron granted {self.potion_yield} Metallicize"

class LiquidBronze(Potion):
    def __init__(self):
        super().__init__("Liquid Bronze", "Uncommon", "The Spire", 3)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Liquid Bronze"
        from game.powers.registry import create_power
        thorns = create_power("Thorns", amount=self.potion_yield)
        player.add_power(thorns)
        self.uses_remaining -= 1
        return f"Liquid Bronze granted {self.potion_yield} Thorns"

class LiquidMemories(Potion):
    def __init__(self):
        super().__init__("Liquid Memories", "Uncommon", "The Spire")

    def use(self, player, entities):
        if not self.can_use(player, entities) or not player.discard_pile:
            return "Cannot use Liquid Memories"
        card_id = random.choice(player.discard_pile)
        player.discard_pile.remove(card_id)
        player.hand.append(f"{card_id}|cost=0")
        self.uses_remaining -= 1
        from game.cards.registry import create_card
        card = create_card(card_id)
        return f"Liquid Memories returned {card.name} to hand (costs 0 energy)"

class RegenPotion(Potion):
    def __init__(self):
        super().__init__("Regen Potion", "Uncommon", "The Spire", 5)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Regen Potion"
        from game.powers.registry import create_power
        regen_power = create_power("Regeneration", amount=self.potion_yield)
        player.add_power(regen_power)
        self.uses_remaining -= 1
        return f"Regen Potion granted {self.potion_yield} Regeneration"

class SmokeBomb(Potion):
    def __init__(self):
        super().__init__("Smoke Bomb", "Rare", "The Spire")

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Smoke Bomb"
        # Escape non-boss combat without rewards
        game_state.end_combat()
        self.uses_remaining -= 1
        return "Smoke Bomb: Escaped combat without rewards"

class SneckoOil(Potion):
    def __init__(self):
        super().__init__("Snecko Oil", "Rare", "The Spire", 5)

    def use(self, player, entities):
        if not self.can_use(player, entities):
            return "Cannot use Snecko Oil"
        player.draw_cards(self.potion_yield)
        # Randomize costs of all cards in hand
        for i, card_id in enumerate(player.hand):
            from game.cards.registry import create_card
            card = create_card(card_id)
            if hasattr(card, 'cost'):
                new_cost = random.randint(0, 3)
                player.hand[i] = f"{card_id}|cost={new_cost}"
        self.uses_remaining -= 1
        return f"Snecko Oil drew {self.potion_yield} cards and randomized costs"

# Potion Factory
def create_potion(potion_name):
    potion_class = Potion._registry.get(potion_name)
    if potion_class:
        return potion_class()
    else:
        return Potion(potion_name)  # Fallback to base potion